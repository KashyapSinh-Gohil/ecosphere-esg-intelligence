from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import csv
import io
import asyncio
import json

from .models import (
    engine, SessionLocal, init_db, Department, Category, 
    EmissionFactor, ProductESGProfile, EnvironmentalGoal,
    ESGPolicy, Badge, Reward, CarbonTransaction, CSRActivity,
    EmployeeParticipation, Challenge, ChallengeParticipation,
    PolicyAcknowledgement, Audit, ComplianceIssue, DepartmentScore,
    OrganizationSetting, EmployeeBalance, RewardRedemption
)
from .schemas import (
    DepartmentCreate, DepartmentResponse, CarbonTransactionCreate, CarbonTransactionResponse,
    RewardResponse, ChallengeResponse, CSRActivityResponse, ComplianceIssueCreate, ComplianceIssueResponse,
    DepartmentScoreResponse
)
from .services import business_rules, iot_stream, forecaster

app = FastAPI(title="EcoSphere ESG Platform API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Department).count() == 0:
            seed_database(db)
        elif db.query(EmployeeBalance).filter(EmployeeBalance.employee_name == "Kashyap S.").first() is None:
            db.add(EmployeeBalance(employee_name="Kashyap S.", xp_total=4820, points_balance=840))
            activities = db.query(CSRActivity).limit(2).all()
            for index, activity in enumerate(activities):
                db.add(EmployeeParticipation(employee_name=["Aditi Rao", "Karan Shah"][index], activity_id=activity.id, proof_file="verified-evidence.pdf", approval_status="pending"))
            db.commit()
    finally:
        db.close()

# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/departments", response_model=list[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@app.get("/emission-factors")
def get_emission_factors(db: Session = Depends(get_db)):
    return db.query(EmissionFactor).all()

@app.get("/environmental-goals")
def get_environmental_goals(db: Session = Depends(get_db)):
    return db.query(EnvironmentalGoal).all()

@app.post("/departments", response_model=DepartmentResponse)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    score = DepartmentScore(department_id=db_dept.id)
    db.add(score)
    db.commit()
    return db_dept

@app.get("/carbon-transactions", response_model=list[CarbonTransactionResponse])
def get_carbon_transactions(db: Session = Depends(get_db)):
    return db.query(CarbonTransaction).order_by(CarbonTransaction.date.desc()).all()

@app.post("/carbon-transactions", response_model=CarbonTransactionResponse)
def create_carbon_transaction(tx: CarbonTransactionCreate, db: Session = Depends(get_db)):
    db_tx = CarbonTransaction(**tx.dict())
    try:
        db_tx = business_rules.handle_auto_emission_calculation(db, db_tx)
        return db_tx
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/department-scores", response_model=list[DepartmentScoreResponse])
def get_department_scores(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    for d in depts:
        business_rules.recalculate_department_scores(db, d.id)
    return db.query(DepartmentScore).all()

@app.get("/rewards", response_model=list[RewardResponse])
def get_rewards(db: Session = Depends(get_db)):
    return db.query(Reward).all()

@app.post("/rewards/redeem")
def redeem_reward(employee_name: str, reward_id: int, db: Session = Depends(get_db)):
    try:
        result = business_rules.redeem_catalog_reward(db, employee_name, reward_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/challenges", response_model=list[ChallengeResponse])
def get_challenges(db: Session = Depends(get_db)):
    return db.query(Challenge).all()

@app.get("/csr-activities", response_model=list[CSRActivityResponse])
def get_csr_activities(db: Session = Depends(get_db)):
    return db.query(CSRActivity).all()

@app.post("/csr-activities")
def create_csr_activity(payload: dict = Body(...), db: Session = Depends(get_db)):
    activity = CSRActivity(
        name=payload.get("name", "New CSR activity"),
        description=payload.get("description", "Employee sustainability activity"),
        xp_reward=int(payload.get("xp_reward", 100)),
        points_reward=int(payload.get("points_reward", 50)),
    )
    db.add(activity); db.commit(); db.refresh(activity)
    return {"id": activity.id, "name": activity.name, "description": activity.description, "xp_reward": activity.xp_reward, "points_reward": activity.points_reward}

@app.get("/participations")
def get_participations(db: Session = Depends(get_db)):
    return [{"id": p.id, "employee_name": p.employee_name, "activity_id": p.activity_id, "activity_name": p.activity.name if p.activity else "Activity", "proof_file": p.proof_file, "approval_status": p.approval_status, "points_earned": p.points_earned} for p in db.query(EmployeeParticipation).all()]

@app.post("/participations")
def join_activity(payload: dict = Body(...), db: Session = Depends(get_db)):
    activity_id = int(payload.get("activity_id"))
    employee = payload.get("employee_name", "Kashyap S.")
    existing = db.query(EmployeeParticipation).filter(EmployeeParticipation.activity_id == activity_id, EmployeeParticipation.employee_name == employee).first()
    if existing:
        return {"id": existing.id, "status": existing.approval_status, "message": "Already joined"}
    if not db.query(CSRActivity).filter(CSRActivity.id == activity_id).first():
        raise HTTPException(404, "Activity not found")
    part = EmployeeParticipation(employee_name=employee, activity_id=activity_id, proof_file=payload.get("proof_file", "self-declaration"), approval_status="pending")
    db.add(part); db.commit(); db.refresh(part)
    return {"id": part.id, "status": part.approval_status, "message": "Activity joined"}

@app.patch("/participations/{participation_id}")
def decide_participation(participation_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        part = business_rules.approve_csr_participation(db, participation_id, payload.get("status", "approved"))
        if part.approval_status == "approved":
            balance = db.query(EmployeeBalance).filter(EmployeeBalance.employee_name == part.employee_name).first()
            if not balance:
                balance = EmployeeBalance(employee_name=part.employee_name, xp_total=0, points_balance=0); db.add(balance)
            balance.points_balance += part.points_earned
            balance.xp_total += (part.activity.xp_reward if part.activity else 100)
            db.commit()
        return {"id": part.id, "status": part.approval_status, "points_earned": part.points_earned}
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@app.get("/compliance-issues", response_model=list[ComplianceIssueResponse])
def get_compliance_issues(db: Session = Depends(get_db)):
    business_rules.check_and_flag_compliance_issues(db)
    return db.query(ComplianceIssue).all()

@app.post("/compliance-issues", response_model=ComplianceIssueResponse)
def create_compliance_issue(issue: ComplianceIssueCreate, db: Session = Depends(get_db)):
    db_issue = ComplianceIssue(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@app.patch("/compliance-issues/{issue_id}")
def update_compliance_issue(issue_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    issue = db.query(ComplianceIssue).filter(ComplianceIssue.id == issue_id).first()
    if not issue: raise HTTPException(404, "Issue not found")
    issue.status = payload.get("status", issue.status)
    db.commit(); db.refresh(issue)
    return issue

@app.get("/policies")
def get_policies(db: Session = Depends(get_db)):
    return db.query(ESGPolicy).all()

@app.get("/audits")
def get_audits(db: Session = Depends(get_db)):
    return db.query(Audit).all()

@app.post("/audits")
def create_audit(payload: dict = Body(...), db: Session = Depends(get_db)):
    audit = Audit(title=payload.get("title", "New ESG audit"), auditor=payload.get("auditor", "Internal ESG team"), findings=payload.get("findings", "Audit scheduled; findings pending."))
    db.add(audit); db.commit(); db.refresh(audit)
    return {"id": audit.id, "title": audit.title, "auditor": audit.auditor, "findings": audit.findings}

@app.get("/balance/{employee_name}")
def get_balance(employee_name: str, db: Session = Depends(get_db)):
    balance = db.query(EmployeeBalance).filter(EmployeeBalance.employee_name == employee_name).first()
    if not balance:
        balance = EmployeeBalance(employee_name=employee_name, xp_total=4820, points_balance=840)
        db.add(balance); db.commit(); db.refresh(balance)
    return {"employee_name": employee_name, "xp_total": balance.xp_total, "points_balance": balance.points_balance}

@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    defaults = {"auto": True, "csr": True, "badges": True, "email": False, "environmental_weight": 40, "social_weight": 30, "governance_weight": 30}
    for setting in db.query(OrganizationSetting).all():
        try: defaults[setting.key] = json.loads(setting.value)
        except Exception: defaults[setting.key] = setting.value
    return defaults

@app.put("/settings")
def save_settings(payload: dict = Body(...), db: Session = Depends(get_db)):
    weights = [int(payload.get("environmental_weight", 40)), int(payload.get("social_weight", 30)), int(payload.get("governance_weight", 30))]
    if sum(weights) != 100: raise HTTPException(400, "ESG weights must total 100%")
    for key, value in payload.items():
        setting = db.query(OrganizationSetting).filter(OrganizationSetting.key == key).first()
        if not setting: setting = OrganizationSetting(key=key, value=json.dumps(value)); db.add(setting)
        else: setting.value = json.dumps(value)
    db.commit()
    return {"status": "saved", **payload}

@app.get("/reports/export")
def export_report(report_type: str = "ESG Summary", db: Session = Depends(get_db)):
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["EcoSphere report", report_type]); writer.writerow(["Generated", datetime.utcnow().isoformat()]); writer.writerow([])
    writer.writerow(["Department", "Environmental", "Social", "Governance", "Total"])
    for score in db.query(DepartmentScore).all():
        writer.writerow([score.department.name if score.department else score.department_id, score.environmental_score, score.social_score, score.governance_score, score.total_score])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=ecosphere-report.csv"})

@app.get("/forecast")
def get_forecast(department_id: Optional[int] = None, days: int = 180, db: Session = Depends(get_db)):
    return forecaster.forecast_emissions(db, department_id, days)

# ==========================================
# WebSocket Stream Endpoint
# ==========================================

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        async for data in iot_stream.generate_iot_telemetry():
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()

# ==========================================
# Database Seeding Utility
# ==========================================

def seed_database(db: Session):
    depts = [
        Department(name="Manufacturing Floor", code="DEPT_MFG", head="Marcus Vance", employee_count=120, status="active"),
        Department(name="Corporate Headquarters", code="DEPT_HQ", head="Sarah Jenkins", employee_count=45, status="active"),
        Department(name="Logistics & Fleet", code="DEPT_LOG", head="Vikram Patel", employee_count=35, status="active"),
        Department(name="Research & Development", code="DEPT_RD", head="Elena Rostova", employee_count=60, status="active")
    ]
    for d in depts:
        db.add(d)
    db.commit()

    for d in depts:
        score = DepartmentScore(
            department_id=d.id,
            environmental_score=92.0 if d.code == "DEPT_HQ" else 78.5,
            social_score=85.0,
            governance_score=90.0,
            total_score=88.0
        )
        db.add(score)
    db.commit()

    factors = [
        EmissionFactor(name="natural_gas", category="stationary_combustion", factor=0.0543, unit="cubic feet"),
        EmissionFactor(name="diesel", category="stationary_combustion", factor=10.21, unit="gallon"),
        EmissionFactor(name="passenger_car", category="mobile_combustion", factor=0.17, unit="km"),
        EmissionFactor(name="light_truck", category="mobile_combustion", factor=0.22, unit="km"),
        EmissionFactor(name="us_national_average", category="indirect_electricity", factor=0.38, unit="kWh"),
        EmissionFactor(name="india_grid", category="indirect_electricity", factor=0.82, unit="kWh"),
        EmissionFactor(name="renewable_ppa", category="indirect_electricity", factor=0.00, unit="kWh"),
    ]
    for f in factors:
        db.add(f)
    db.commit()

    activities = [
        CSRActivity(name="Annual Tree Plantation Drive", description="Plant trees in local park.", xp_reward=200, points_reward=100),
        CSRActivity(name="Corporate Wellness Run", description="5k marathon.", xp_reward=100, points_reward=50),
        CSRActivity(name="Office Recycling Workshop", description="Segregation workshop.", xp_reward=120, points_reward=60),
    ]
    for a in activities:
        db.add(a)
    db.commit()

    db.add(EmployeeParticipation(employee_name="Aditi Rao", activity_id=activities[0].id, proof_file="tree-plantation-proof.jpg", approval_status="pending"))
    db.add(EmployeeParticipation(employee_name="Karan Shah", activity_id=activities[2].id, proof_file="training-certificate.pdf", approval_status="pending"))
    db.add(EmployeeBalance(employee_name="Kashyap S.", xp_total=4820, points_balance=840))
    db.add(EnvironmentalGoal(title="Reduce fleet emissions", target_value=500, current_value=390, deadline=datetime(2026, 12, 31), status="active"))
    db.add(EnvironmentalGoal(title="Cut packaging waste", target_value=120, current_value=98, deadline=datetime(2026, 9, 30), status="at_risk"))
    db.add(ESGPolicy(title="Environmental Commitment", content="Acme Industries commits to measurable, evidence-backed emissions reduction."))
    db.add(ESGPolicy(title="Supplier Code of Conduct", content="Suppliers must meet environmental, labor, and governance requirements."))
    db.commit()

    challenges = [
        Challenge(title="Zero Single-Use Plastics Week", category="Social", description="Avoid plastics.", xp=250, difficulty="Medium", evidence_required=True, deadline=datetime.utcnow() + timedelta(days=7), status="Active"),
        Challenge(title="EV Carpooling Initiative", category="Environmental", description="EV carpool.", xp=400, difficulty="Hard", evidence_required=True, deadline=datetime.utcnow() + timedelta(days=14), status="Active"),
    ]
    for c in challenges:
        db.add(c)
    db.commit()

    badges = [
        Badge(name="Carbon Sentinel", description="Awarded for 500+ XP.", unlock_rule="xp >= 500", icon="shield"),
        Badge(name="Eco-Pioneer", description="Awarded for 3+ CSR activities.", unlock_rule="challenges >= 3", icon="sprout")
    ]
    for b in badges:
        db.add(b)
    db.commit()

    rewards = [
        Reward(name="Eco Coffee Tumbler", description="Ocean bound plastics flask.", points_required=150, stock=25, status="active"),
        Reward(name="Plantable Seed Notebook", description="Recycled seed notebook.", points_required=80, stock=40, status="active"),
        Reward(name="Extra Paid Leave Day", description="1 paid leaf day.", points_required=500, stock=5, status="active"),
    ]
    for r in rewards:
        db.add(r)
    db.commit()

    mfg_dept = depts[0]
    fleet_dept = depts[2]
    elec_factor = factors[4]
    gas_factor = factors[0]

    for day_offset in range(10, 0, -1):
        date = datetime.utcnow() - timedelta(days=day_offset)
        tx1 = CarbonTransaction(
            source_type="manufacturing",
            activity_amount=2000.0 + (day_offset * 150),
            emission_factor_id=elec_factor.id,
            calculated_co2e=(2000.0 + (day_offset * 150)) * elec_factor.factor,
            date=date,
            department_id=mfg_dept.id
        )
        tx2 = CarbonTransaction(
            source_type="fleet",
            activity_amount=400.0 + (day_offset * 20),
            emission_factor_id=gas_factor.id,
            calculated_co2e=(400.0 + (day_offset * 20)) * gas_factor.factor,
            date=date,
            department_id=fleet_dept.id
        )
        db.add(tx1)
        db.add(tx2)
    db.commit()

    audit = Audit(title="Q2 Annual Environment Audit", auditor="GreenTech Auditing Ltd", findings="Some minor deviations observed.")
    db.add(audit)
    db.commit()

    issue = ComplianceIssue(
        audit_id=audit.id,
        severity="Medium",
        description="Hazardous labeling not compliant.",
        owner="Vikram Patel",
        due_date=datetime.utcnow() - timedelta(days=2),
        status="Open"
    )
    db.add(issue)
    db.commit()

# ==========================================
# Frontend Static Files Serving
# ==========================================
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

if os.path.isdir(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/")
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str = ""):
        # Avoid intercepting API routes
        if catchall.startswith("ws/") or catchall in ["departments", "carbon-transactions", "department-scores", "rewards", "challenges", "csr-activities", "compliance-issues", "forecast"]:
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(frontend_path, "index.html"))
