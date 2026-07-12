from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import json

from .models import (
    engine, SessionLocal, init_db, Department, Category, 
    EmissionFactor, ProductESGProfile, EnvironmentalGoal,
    ESGPolicy, Badge, Reward, CarbonTransaction, CSRActivity,
    EmployeeParticipation, Challenge, ChallengeParticipation,
    PolicyAcknowledgement, Audit, ComplianceIssue, DepartmentScore
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
    finally:
        db.close()

# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/departments", response_model=list[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

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
