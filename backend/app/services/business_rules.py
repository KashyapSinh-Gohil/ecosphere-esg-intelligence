from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..models import (
    CarbonTransaction, EmissionFactor, EmployeeParticipation, 
    CSRActivity, Badge, Reward, ChallengeParticipation, Challenge,
    ComplianceIssue, DepartmentScore, Department, EmployeeBalance, RewardRedemption
)
from calculators import scope1_direct, scope2_indirect, scope3_supply

# Configurations
CONFIG_AUTO_EMISSION = True
CONFIG_EVIDENCE_REQUIRED = True
CONFIG_BADGE_AUTO_AWARD = True

def handle_auto_emission_calculation(db: Session, tx: CarbonTransaction) -> CarbonTransaction:
    """
    Business Rule: Auto Emission Calculation
    Intercepts CarbonTransaction and calculates CO2e based on the selected EmissionFactor.
    """
    if not CONFIG_AUTO_EMISSION:
        return tx

    factor_obj = db.query(EmissionFactor).filter(EmissionFactor.id == tx.emission_factor_id).first()
    if not factor_obj:
        raise ValueError(f"Emission Factor ID {tx.emission_factor_id} not found")

    cat = factor_obj.category.lower()
    qty = tx.activity_amount
    co2e = 0.0

    if cat == "stationary_combustion":
        co2e = scope1_direct.calculate_stationary_combustion(factor_obj.name, qty)
    elif cat == "mobile_combustion":
        co2e = scope1_direct.calculate_mobile_combustion(factor_obj.name, qty)
    elif cat == "indirect_electricity":
        co2e = scope2_indirect.calculate_purchased_electricity(qty, factor_obj.name)
    elif cat == "freight":
        co2e = qty * factor_obj.factor
    else:
        co2e = qty * factor_obj.factor

    tx.calculated_co2e = co2e
    db.add(tx)
    db.commit()
    db.refresh(tx)

    recalculate_department_scores(db, tx.department_id)
    return tx

def approve_csr_participation(db: Session, part_id: int, approver_status: str) -> EmployeeParticipation:
    """
    Business Rule: Evidence Requirement & Approval Workflow
    Validates that approved CSR participations have proof attached. Awards XP/Points upon approval.
    """
    part = db.query(EmployeeParticipation).filter(EmployeeParticipation.id == part_id).first()
    if not part:
        raise ValueError("Participation not found")

    if approver_status.lower() == "approved":
        if CONFIG_EVIDENCE_REQUIRED and not part.proof_file:
            raise ValueError("Evidence file/proof is required for approval")

        part.approval_status = "approved"
        activity = db.query(CSRActivity).filter(CSRActivity.id == part.activity_id).first()
        if activity:
            part.points_earned = activity.points_reward
            if CONFIG_BADGE_AUTO_AWARD:
                auto_award_badges(db, part.employee_name)
    else:
        part.approval_status = "rejected"
        part.points_earned = 0

    db.commit()
    db.refresh(part)
    return part

def redeem_catalog_reward(db: Session, employee_name: str, reward_id: int) -> dict:
    """
    Business Rule: Reward Redemption & Stock Checks
    Deducts points and stock atomically.
    """
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status != "active" or reward.stock <= 0:
        raise ValueError("Reward is out of stock or inactive")

    balance = db.query(EmployeeBalance).filter(EmployeeBalance.employee_name == employee_name).first()
    if not balance:
        earned = db.query(func.sum(EmployeeParticipation.points_earned)).filter(
            EmployeeParticipation.employee_name == employee_name,
            EmployeeParticipation.approval_status == "approved"
        ).scalar() or 0
        balance = EmployeeBalance(employee_name=employee_name, points_balance=int(earned), xp_total=int(earned) * 2)
        db.add(balance)
        db.flush()

    if balance.points_balance < reward.points_required:
        raise ValueError(f"Insufficient points. Required: {reward.points_required}, Available: {balance.points_balance}")

    reward.stock -= 1
    balance.points_balance -= reward.points_required
    db.add(RewardRedemption(employee_name=employee_name, reward_id=reward.id, points_spent=reward.points_required))
    db.commit()
    db.refresh(reward)

    return {
        "status": "success",
        "message": f"Successfully redeemed {reward.name}",
        "remaining_stock": reward.stock,
        "points_balance": balance.points_balance,
    }

def auto_award_badges(db: Session, employee_name: str) -> list:
    """
    Business Rule: Badge Auto-Award
    Awards badges automatically when employee metrics meet unlock rules.
    """
    total_xp = db.query(EmployeeParticipation).filter(
        EmployeeParticipation.employee_name == employee_name,
        EmployeeParticipation.approval_status == "approved"
    ).count() * 100

    challenges_done = db.query(ChallengeParticipation).filter(
        ChallengeParticipation.employee_name == employee_name,
        ChallengeParticipation.approval_status == "approved"
    ).count()

    badges = db.query(Badge).all()
    awarded = []

    for badge in badges:
        rule = badge.unlock_rule.lower()
        qualified = False
        if "xp" in rule:
            try:
                target_xp = int(rule.split(">=")[1].strip())
                if total_xp >= target_xp:
                    qualified = True
            except Exception:
                pass
        elif "challenges" in rule:
            try:
                target_challenges = int(rule.split(">=")[1].strip())
                if challenges_done >= target_challenges:
                    qualified = True
            except Exception:
                pass
        
        if qualified:
            awarded.append(badge.name)

    return awarded

def check_and_flag_compliance_issues(db: Session):
    """
    Business Rule: Compliance Issue Ownership & Due Date Flagging
    Flags issues that are open and past their due date.
    """
    now = datetime.utcnow()
    overdue_issues = db.query(ComplianceIssue).filter(
        ComplianceIssue.status == "Open",
        ComplianceIssue.due_date < now
    ).all()

    for issue in overdue_issues:
        issue.status = "Flagged"
    
    db.commit()

def recalculate_department_scores(db: Session, department_id: int):
    """
    Recalculates the environmental, social, and governance scores for a department.
    """
    score = db.query(DepartmentScore).filter(DepartmentScore.department_id == department_id).first()
    if not score:
        score = DepartmentScore(department_id=department_id)
        db.add(score)

    total_emissions = db.query(func.sum(CarbonTransaction.calculated_co2e)).filter(
        CarbonTransaction.department_id == department_id
    ).scalar() or 0.0

    # Basic scoring logic
    if total_emissions > 5000:
        score.environmental_score = max(50.0, 100.0 - ((total_emissions - 5000) / 100))
    else:
        score.environmental_score = 90.0 + (5000 - total_emissions) / 500

    dept = db.query(Department).filter(Department.id == department_id).first()
    emp_count = dept.employee_count if dept else 10
    
    approved_parts = db.query(EmployeeParticipation).join(CSRActivity).filter(
        EmployeeParticipation.approval_status == "approved"
    ).count()

    score.social_score = min(100.0, round(60.0 + (approved_parts * 5.0 / max(1, emp_count / 10)), 1))

    open_issues = db.query(ComplianceIssue).filter(
        ComplianceIssue.status.in_(["Open", "Flagged"])
    ).count()
    score.governance_score = max(20.0, round(100.0 - (open_issues * 15.0), 1))

    score.total_score = round(
        (score.environmental_score * 0.4) +
        (score.social_score * 0.3) +
        (score.governance_score * 0.3),
        1
    )
    db.commit()
