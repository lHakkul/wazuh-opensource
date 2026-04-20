from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    UNKNOWN = "unknown"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    NEVER_CONNECTED = "never_connected"


class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus
    details: Optional[dict] = None


class HealthScoreItem(BaseModel):
    name: str
    label: str
    score: int
    weight: int
    status: HealthStatus
    detail: Optional[str] = None


class HealthScore(BaseModel):
    score: int
    status: HealthStatus
    summary: str
    backend_errors_recent: int = 0
    api_latency_ms: Optional[float] = None
    breakdown: List[HealthScoreItem]


class SlaMetric(BaseModel):
    name: str
    label: str
    availability: float
    window_hours: int
    status: HealthStatus
    detail: Optional[str] = None


class SlaSummary(BaseModel):
    metrics: List[SlaMetric]


class ClusterNode(BaseModel):
    name: str
    type: str
    version: str
    address: str
    status: str


class ClusterHealth(BaseModel):
    status: HealthStatus
    enabled: bool
    running: bool
    nodes: Optional[List[ClusterNode]] = None
    raw: Optional[dict] = None


class Agent(BaseModel):
    id: str
    name: str
    ip: Optional[str] = None
    status: AgentStatus
    version: Optional[str] = None
    os_name: Optional[str] = None
    os_platform: Optional[str] = None
    last_keepalive: Optional[str] = None
    manager: Optional[str] = None
    group: Optional[List[str]] = None


class AgentsSummary(BaseModel):
    total: int
    active: int
    disconnected: int
    pending: int
    never_connected: int
    agents: List[Agent]


class ManagerStatus(BaseModel):
    status: HealthStatus
    enabled: List[str]
    running: List[str]
    stopped: List[str]
    raw: Optional[dict] = None


class IndexerHealth(BaseModel):
    status: HealthStatus
    cluster_name: Optional[str] = None
    number_of_nodes: Optional[int] = None
    active_shards: Optional[int] = None
    raw: Optional[dict] = None


class OverviewHealth(BaseModel):
    timestamp: datetime
    global_status: HealthStatus
    cluster: Optional[ClusterHealth] = None
    manager: Optional[ManagerStatus] = None
    indexer: Optional[IndexerHealth] = None
    agents: Optional[AgentsSummary] = None
    components: List[ComponentHealth] = []
    health_score: Optional[HealthScore] = None
    sla: Optional[SlaSummary] = None


class HistoryEvent(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    severity: HealthStatus
    component: str
    message: str
    details: Optional[dict] = None


class AlertConfig(BaseModel):
    telegram_enabled: bool
    slack_enabled: bool
