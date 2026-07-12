from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ==========================================
# Department Schemas
# ==========================================
class DepartmentBase(BaseModel):
    name: str
    code: str
    head: Optional[str] = None
    parent_department_id: Optional[int] = None
    employee_count: int = 0
    status: str = "active"

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Category Schemas
# ==========================================
class CategoryBase(BaseModel):
    name: str
    type: str
    status: str = "active"

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Emission Factor Schemas
# ==========================================
class EmissionFactorBase(BaseModel):
    name: str
    category: str
    factor: float
    unit: str

class EmissionFactorCreate(EmissionFactorBase):
    pass

class EmissionFactorResponse(EmissionFactorBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Product ESG Profile Schemas
# ==========================================
class ProductESGProfileBase(BaseModel):
    product_name: str
    carbon_footprint: float = 0.0
    sustainability_rating: str = "C"

class ProductESGProfileCreate(ProductESGProfileBase):
    pass

class ProductESGProfileResponse(ProductESGProfileBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Environmental Goal Schemas
# ==========================================
class EnvironmentalGoalBase(BaseModel):
    title: str
    target_value: float
    current_value: float = 0.0
    deadline: datetime
    status: str = "active"

class EnvironmentalGoalCreate(EnvironmentalGoalBase):
    pass

class EnvironmentalGoalResponse(EnvironmentalGoalBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# ESG Policy Schemas
# ==========================================
class ESGPolicyBase(BaseModel):
    title: str
    content: str
    published_date: Optional[datetime] = None

class ESGPolicyCreate(ESGPolicyBase):
    pass

class ESGPolicyResponse(ESGPolicyBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Badge Schemas
# ==========================================
class BadgeBase(BaseModel):
    name: str
    description: str
    unlock_rule: str
    icon: str

class BadgeCreate(BadgeBase):
    pass

class BadgeResponse(BadgeBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Reward Schemas
# ==========================================
class RewardBase(BaseModel):
    name: str
    description: str
    points_required: int
    stock: int = 0
    status: str = "active"

class RewardCreate(RewardBase):
    pass

class RewardResponse(RewardBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Carbon Transaction Schemas
# ==========================================
class CarbonTransactionBase(BaseModel):
    source_type: str
    activity_amount: float
    emission_factor_id: int
    department_id: int
    date: Optional[datetime] = None

class CarbonTransactionCreate(CarbonTransactionBase):
    pass

class CarbonTransactionResponse(CarbonTransactionBase):
    id: int
    calculated_co2e: float
    date: datetime
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# CSR Activity Schemas
# ==========================================
class CSRActivityBase(BaseModel):
    name: str
    description: str
    xp_reward: int = 100
    points_reward: int = 50

class CSRActivityCreate(CSRActivityBase):
    pass

class CSRActivityResponse(CSRActivityBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Employee Participation Schemas
# ==========================================
class EmployeeParticipationBase(BaseModel):
    employee_name: str
    activity_id: int
    proof_file: Optional[str] = None
    approval_status: str = "pending"
    points_earned: int = 0
    completion_date: Optional[datetime] = None

class EmployeeParticipationCreate(EmployeeParticipationBase):
    pass

class EmployeeParticipationResponse(EmployeeParticipationBase):
    id: int
    completion_date: datetime
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Challenge Schemas
# ==========================================
class ChallengeBase(BaseModel):
    title: str
    category: str
    description: str
    xp: int = 200
    difficulty: str = "Medium"
    evidence_required: bool = True
    deadline: datetime
    status: str = "Draft"

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeResponse(ChallengeBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Challenge Participation Schemas
# ==========================================
class ChallengeParticipationBase(BaseModel):
    challenge_id: int
    employee_name: str
    progress: float = 0.0
    proof_file: Optional[str] = None
    approval_status: str = "pending"
    xp_awarded: int = 0

class ChallengeParticipationCreate(ChallengeParticipationBase):
    pass

class ChallengeParticipationResponse(ChallengeParticipationBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Policy Acknowledgement Schemas
# ==========================================
class PolicyAcknowledgementBase(BaseModel):
    policy_id: int
    employee_name: str

class PolicyAcknowledgementCreate(PolicyAcknowledgementBase):
    pass

class PolicyAcknowledgementResponse(PolicyAcknowledgementBase):
    id: int
    acknowledged_date: datetime
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Audit Schemas
# ==========================================
class AuditBase(BaseModel):
    title: str
    auditor: str
    findings: str
    audit_date: Optional[datetime] = None

class AuditCreate(AuditBase):
    pass

class AuditResponse(AuditBase):
    id: int
    audit_date: datetime
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Compliance Issue Schemas
# ==========================================
class ComplianceIssueBase(BaseModel):
    audit_id: int
    severity: str
    description: str
    owner: str
    due_date: datetime
    status: str = "Open"

class ComplianceIssueCreate(ComplianceIssueBase):
    pass

class ComplianceIssueResponse(ComplianceIssueBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

# ==========================================
# Department Score Schemas
# ==========================================
class DepartmentScoreBase(BaseModel):
    department_id: int
    environmental_score: float = 100.0
    social_score: float = 100.0
    governance_score: float = 100.0
    total_score: float = 100.0

class DepartmentScoreResponse(DepartmentScoreBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True
