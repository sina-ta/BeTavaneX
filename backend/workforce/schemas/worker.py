from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class WorkerScores(BaseModel):
    productivity_score: Optional[float] = None
    reliability_score: Optional[float] = None
    safety_score: Optional[float] = None
    teamwork_score: Optional[float] = None
    quality_score: Optional[float] = None
    leadership_score: Optional[float] = None


class WorkerListItem(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    trade: str
    current_role: Optional[str] = None
    crew: Optional[str] = None
    skill_level: Optional[str] = None
    availability_status: str
    daily_cost: Optional[float] = None
    scores: WorkerScores
    assignment_readiness: str
    is_active: bool


class WorkerDetail(WorkerListItem):
    phone: Optional[str] = None
    current_project_id: Optional[int] = None
    safety_clearance: Optional[str] = None
    skills: list[str] = []
    certifications: list[str] = []


class CrewSummary(BaseModel):
    id: int
    name: str
    trade: Optional[str] = None
    supervisor: Optional[str] = None
    active_project_id: Optional[int] = None
    performance_score: Optional[float] = None
    utilization_rate: Optional[float] = None
    worker_count: int = 0


class WorkforceAnalyticsResponse(BaseModel):
    total_workers: int
    available_workers: int
    assigned_workers: int
    avg_productivity_score: Optional[float] = None
    avg_reliability_score: Optional[float] = None
    crew_count: int
    trend: str
    workers: list[dict] = []


class WorkerIntelligenceResponse(BaseModel):
    worker_id: int
    full_name: str
    trade: str
    crew: Optional[str] = None
    availability_status: str
    scores: WorkerScores
    operational_signals: list[dict] = []
    daily_report_contribution: dict = {}
    assignment_count: int = 0
    eligibility_summary: dict = {}


class EligibilityCheckResponse(BaseModel):
    worker_id: int
    task_id: Optional[int] = None
    eligible: bool
    factors: list[dict]
