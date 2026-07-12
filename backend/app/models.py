import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./ecosphere_esg.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# Master Data Models
# ==========================================

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)
    head = Column(String)
    parent_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    employee_count = Column(Integer, default=0)
    status = Column(String, default="active") # active, inactive

    parent = relationship("Department", remote_side=[id])
    scores = relationship("DepartmentScore", back_populates="department")
    carbon_transactions = relationship("CarbonTransaction", back_populates="department")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True) # "CSR Activity", "Challenge", "Emission Factor"
    status = Column(String, default="active")

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g. "Natural Gas", "Grid Electricity EU", "Passenger Car"
    category = Column(String, index=True) # stationary_combustion, mobile_combustion, indirect_electricity, freight, travel
    factor = Column(Float, nullable=False) # kg CO2e per unit
    unit = Column(String, nullable=False) # e.g. "gallon", "kWh", "passenger-km", "ton-km"

class ProductESGProfile(Base):
    __tablename__ = "product_esg_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, index=True)
    carbon_footprint = Column(Float, default=0.0) # kg CO2e per product unit
    sustainability_rating = Column(String, default="C") # A, B, C, D, E, F

class EnvironmentalGoal(Base):
    __tablename__ = "environmental_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    target_value = Column(Float, nullable=False) # target emissions (kg CO2e)
    current_value = Column(Float, default=0.0)
    deadline = Column(DateTime)
    status = Column(String, default="active") # active, completed, failed

class ESGPolicy(Base):
    __tablename__ = "esg_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    content = Column(Text, nullable=False)
    published_date = Column(DateTime, default=datetime.utcnow)

    acknowledgements = relationship("PolicyAcknowledgement", back_populates="policy")

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    unlock_rule = Column(String) # e.g., "xp >= 500", "challenges_completed >= 5"
    icon = Column(String) # icon code or name

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    points_required = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    status = Column(String, default="active") # active, inactive

# ==========================================
# Transactional Data Models
# ==========================================

class CarbonTransaction(Base):
    __tablename__ = "carbon_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, index=True) # "purchase", "manufacturing", "expense", "fleet"
    activity_amount = Column(Float, nullable=False) # quantity consumed
    emission_factor_id = Column(Integer, ForeignKey("emission_factors.id"))
    calculated_co2e = Column(Float, default=0.0) # calculated kg CO2e
    date = Column(DateTime, default=datetime.utcnow)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="carbon_transactions")
    emission_factor = relationship("EmissionFactor")

class CSRActivity(Base):
    __tablename__ = "csr_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    xp_reward = Column(Integer, default=100)
    points_reward = Column(Integer, default=50)

    participations = relationship("EmployeeParticipation", back_populates="activity")

class EmployeeParticipation(Base):
    __tablename__ = "employee_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, index=True)
    activity_id = Column(Integer, ForeignKey("csr_activities.id"))
    proof_file = Column(String, nullable=True) # relative path or filename
    approval_status = Column(String, default="pending") # pending, approved, rejected
    points_earned = Column(Integer, default=0)
    completion_date = Column(DateTime, default=datetime.utcnow)

    activity = relationship("CSRActivity", back_populates="participations")

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    description = Column(String)
    xp = Column(Integer, default=200)
    difficulty = Column(String, default="Medium") # Easy, Medium, Hard
    evidence_required = Column(Boolean, default=True)
    deadline = Column(DateTime)
    status = Column(String, default="Draft") # Draft, Active, Under Review, Completed, Archived

    participations = relationship("ChallengeParticipation", back_populates="challenge")

class ChallengeParticipation(Base):
    __tablename__ = "challenge_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    employee_name = Column(String, index=True)
    progress = Column(Float, default=0.0) # 0.0 to 100.0
    proof_file = Column(String, nullable=True)
    approval_status = Column(String, default="pending") # pending, approved, rejected
    xp_awarded = Column(Integer, default=0)

    challenge = relationship("Challenge", back_populates="participations")

class PolicyAcknowledgement(Base):
    __tablename__ = "policy_acknowledgements"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("esg_policies.id"))
    employee_name = Column(String, index=True)
    acknowledged_date = Column(DateTime, default=datetime.utcnow)

    policy = relationship("ESGPolicy", back_populates="acknowledgements")

class Audit(Base):
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    audit_date = Column(DateTime, default=datetime.utcnow)
    auditor = Column(String)
    findings = Column(Text)

    compliance_issues = relationship("ComplianceIssue", back_populates="audit")

class ComplianceIssue(Base):
    __tablename__ = "compliance_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"))
    severity = Column(String, index=True) # Low, Medium, High, Critical
    description = Column(Text)
    owner = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="Open") # Open, Flagged, Resolved

    audit = relationship("Audit", back_populates="compliance_issues")

class DepartmentScore(Base):
    __tablename__ = "department_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    environmental_score = Column(Float, default=100.0)
    social_score = Column(Float, default=100.0)
    governance_score = Column(Float, default=100.0)
    total_score = Column(Float, default=100.0)

    department = relationship("Department", back_populates="scores")

class OrganizationSetting(Base):
    __tablename__ = "organization_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmployeeBalance(Base):
    __tablename__ = "employee_balances"

    id = Column(Integer, primary_key=True)
    employee_name = Column(String, unique=True, index=True, nullable=False)
    xp_total = Column(Integer, default=0, nullable=False)
    points_balance = Column(Integer, default=0, nullable=False)

class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    id = Column(Integer, primary_key=True)
    employee_name = Column(String, index=True, nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
