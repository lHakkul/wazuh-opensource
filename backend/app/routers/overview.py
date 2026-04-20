from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import time

from app.config import settings
from app.services import wazuh, alerts, history
from app.models.schemas import (
    OverviewHealth, ComponentHealth, HealthStatus,
    ClusterHealth, ClusterNode, ManagerStatus, AgentsSummary, Agent, AgentStatus,
    IndexerHealth, HealthScore, HealthScoreItem, SlaMetric, SlaSummary
)

router = APIRouter(prefix="/api/overview", tags=["overview"])

CRITICAL_DAEMONS = {
    "wazuh-analysisd",
    "wazuh-remoted",
    "wazuh-db",
    "wazuh-apid",
    "wazuh-execd",
}


def _normalize_daemon(name: str) -> str:
    return name.replace("_", "-")


def _determine_global_status(statuses: List[HealthStatus]) -> HealthStatus:
    if HealthStatus.RED in statuses or HealthStatus.UNKNOWN in statuses:
        return HealthStatus.RED
    if HealthStatus.YELLOW in statuses:
        return HealthStatus.YELLOW
    if all(s == HealthStatus.GREEN for s in statuses):
        return HealthStatus.GREEN
    return HealthStatus.UNKNOWN


def _parse_cluster(raw: dict) -> ClusterHealth:
    enabled = raw.get("enabled", True)

    if not enabled:
        return ClusterHealth(status=HealthStatus.GREEN, enabled=False, running=False, nodes=[])

    nodes_raw = raw.get("nodes", {}).get("data", {}).get("affected_items", [])
    nodes = [
        ClusterNode(
            name=n.get("name", ""),
            type=n.get("type", ""),
            version=n.get("version", ""),
            address=n.get("ip", ""),
            status=n.get("status", ""),
        )
        for n in nodes_raw
    ]
    active = [n for n in nodes if n.status == "connected"]
    if not nodes:
        status = HealthStatus.GREEN
    elif len(active) == len(nodes):
        status = HealthStatus.GREEN
    elif active:
        status = HealthStatus.YELLOW
    else:
        status = HealthStatus.RED

    return ClusterHealth(status=status, enabled=True, running=bool(active), nodes=nodes)


def _parse_manager(raw: dict) -> ManagerStatus:
    data = {}
    items = raw.get("data", {}).get("affected_items", [])
    if items:
        data = items[0]

    running = [k for k, v in data.items() if v == "running"]
    stopped = [k for k, v in data.items() if v == "stopped"]
    enabled = running + stopped

    if not data:
        health = HealthStatus.UNKNOWN
    elif stopped:
        health = HealthStatus.YELLOW if running else HealthStatus.RED
    else:
        health = HealthStatus.GREEN

    return ManagerStatus(status=health, enabled=enabled, running=running, stopped=stopped)


def _parse_agents(raw: dict) -> AgentsSummary:
    items = raw.get("data", {}).get("affected_items", [])
    agents = []
    for item in items:
        os_info = item.get("os") or {}
        s = item.get("status", "never_connected").lower().replace(" ", "_")
        try:
            status = AgentStatus(s)
        except ValueError:
            status = AgentStatus.NEVER_CONNECTED
        agents.append(Agent(
            id=str(item.get("id", "")),
            name=item.get("name", ""),
            ip=item.get("ip"),
            status=status,
            version=item.get("version"),
            os_name=os_info.get("name"),
            os_platform=os_info.get("platform"),
            last_keepalive=item.get("lastKeepAlive"),
            manager=item.get("manager"),
            group=item.get("group"),
        ))

    active = sum(1 for a in agents if a.status == AgentStatus.ACTIVE)
    disconnected = sum(1 for a in agents if a.status == AgentStatus.DISCONNECTED)
    pending = sum(1 for a in agents if a.status == AgentStatus.PENDING)
    never = sum(1 for a in agents if a.status == AgentStatus.NEVER_CONNECTED)

    return AgentsSummary(
        total=len(agents),
        active=active,
        disconnected=disconnected,
        pending=pending,
        never_connected=never,
        agents=agents,
    )


def _parse_indexer(raw: dict) -> IndexerHealth:
    if not raw:
        return IndexerHealth(status=HealthStatus.UNKNOWN)

    data = raw.get("data", {})
    affected = data.get("affected_items", [])
    indexer_config = affected[0] if affected else data
    if isinstance(indexer_config, dict) and "indexer" in indexer_config:
        indexer_config = indexer_config["indexer"]
    hosts = indexer_config.get("hosts") or indexer_config.get("nodes") or []

    status = HealthStatus.GREEN if hosts or data else HealthStatus.YELLOW
    return IndexerHealth(
        status=status,
        cluster_name=indexer_config.get("cluster_name"),
        number_of_nodes=len(hosts) if isinstance(hosts, list) else None,
        raw=raw,
    )


async def _timed(name: str, coro):
    started = time.perf_counter()
    try:
        data = await coro
        return {
            "name": name,
            "data": data,
            "error": None,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:
        return {
            "name": name,
            "data": None,
            "error": exc,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def _status_from_score(score: int) -> HealthStatus:
    if score >= 90:
        return HealthStatus.GREEN
    if score >= 70:
        return HealthStatus.YELLOW
    return HealthStatus.RED


def _component_score(status: Optional[HealthStatus], *, unknown_score: int = 0) -> int:
    if status == HealthStatus.GREEN:
        return 100
    if status == HealthStatus.YELLOW:
        return 65
    if status == HealthStatus.RED:
        return 0
    return unknown_score


def _health_status_for_percentage(value: float, yellow_at: float = 90.0) -> HealthStatus:
    if value >= 99.0:
        return HealthStatus.GREEN
    if value >= yellow_at:
        return HealthStatus.YELLOW
    return HealthStatus.RED


def _build_health_score(
    components: List[ComponentHealth],
    manager: Optional[ManagerStatus],
    cluster: Optional[ClusterHealth],
    indexer: Optional[IndexerHealth],
    agents: Optional[AgentsSummary],
    timings: List[dict],
) -> HealthScore:
    component_map = {c.name: c for c in components}
    backend_errors = sum(1 for t in timings if t.get("error"))
    latencies = [t["duration_ms"] for t in timings if t.get("duration_ms") is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    api_status = component_map.get("wazuh_api", ComponentHealth(name="wazuh_api", status=HealthStatus.UNKNOWN)).status
    manager_score = _component_score(manager.status if manager else HealthStatus.UNKNOWN, unknown_score=20)

    running = {_normalize_daemon(d) for d in (manager.running if manager else [])}
    enabled = {_normalize_daemon(d) for d in (manager.enabled if manager else [])}
    expected_critical = CRITICAL_DAEMONS.intersection(enabled) or CRITICAL_DAEMONS
    critical_running = len(expected_critical.intersection(running))
    critical_score = round((critical_running / len(expected_critical)) * 100) if expected_critical else 100

    if agents and agents.total:
        agent_score = round((agents.active / agents.total) * 100)
        agent_detail = f"{agents.active}/{agents.total} agentes activos"
    elif agents:
        agent_score = 100
        agent_detail = "Sin agentes registrados"
    else:
        agent_score = 0
        agent_detail = "No se pudo consultar agentes"

    indexer_score = _component_score(indexer.status if indexer else HealthStatus.UNKNOWN, unknown_score=40)
    cluster_score = _component_score(cluster.status if cluster else HealthStatus.UNKNOWN, unknown_score=30)

    if avg_latency is None:
        latency_score = 0
        latency_detail = "Sin medición de latencia"
    elif avg_latency <= 500:
        latency_score = 100
        latency_detail = f"{avg_latency} ms promedio"
    elif avg_latency <= 1500:
        latency_score = 70
        latency_detail = f"{avg_latency} ms promedio"
    elif avg_latency <= 3000:
        latency_score = 40
        latency_detail = f"{avg_latency} ms promedio"
    else:
        latency_score = 10
        latency_detail = f"{avg_latency} ms promedio"

    error_score = 100 if backend_errors == 0 else max(0, 100 - backend_errors * 35)

    items = [
        HealthScoreItem(name="wazuh_api", label="API Wazuh accesible", score=_component_score(api_status), weight=15, status=api_status),
        HealthScoreItem(name="manager", label="Manager operativo", score=manager_score, weight=20, status=manager.status if manager else HealthStatus.UNKNOWN),
        HealthScoreItem(
            name="critical_daemons",
            label="Daemons críticos activos",
            score=critical_score,
            weight=20,
            status=_health_status_for_percentage(critical_score, yellow_at=80),
            detail=f"{critical_running}/{len(expected_critical)} críticos running",
        ),
        HealthScoreItem(
            name="agents",
            label="Agentes conectados",
            score=agent_score,
            weight=15,
            status=_health_status_for_percentage(agent_score, yellow_at=80),
            detail=agent_detail,
        ),
        HealthScoreItem(name="indexer", label="Indexer disponible", score=indexer_score, weight=10, status=indexer.status if indexer else HealthStatus.UNKNOWN),
        HealthScoreItem(name="cluster", label="Cluster sano", score=cluster_score, weight=10, status=cluster.status if cluster else HealthStatus.UNKNOWN),
        HealthScoreItem(name="latency", label="Latencia de consultas", score=latency_score, weight=5, status=_status_from_score(latency_score), detail=latency_detail),
        HealthScoreItem(name="backend_errors", label="Errores recientes backend", score=error_score, weight=5, status=_status_from_score(error_score), detail=f"{backend_errors} errores en último polling"),
    ]

    weighted = sum(item.score * item.weight for item in items) / sum(item.weight for item in items)
    score = round(weighted)
    status = _status_from_score(score)

    if status == HealthStatus.GREEN:
        summary = "Ecosistema Wazuh saludable"
    elif status == HealthStatus.YELLOW:
        summary = "Ecosistema Wazuh degradado"
    else:
        summary = "Ecosistema Wazuh en riesgo operativo"

    return HealthScore(
        score=score,
        status=status,
        summary=summary,
        backend_errors_recent=backend_errors,
        api_latency_ms=avg_latency,
        breakdown=items,
    )


def _availability_from_history(component: str, current_status: HealthStatus, window_hours: int) -> float:
    window_start = datetime.utcnow() - timedelta(hours=window_hours)
    events = [
        e for e in history.get_events_since(window_hours)
        if e.component == component and e.event_type == "status_change"
    ]
    events.sort(key=lambda e: e.timestamp)

    if not events:
        return 100.0 if current_status in (HealthStatus.GREEN, HealthStatus.YELLOW) else 0.0

    status = events[0].severity
    cursor = window_start
    up_seconds = 0.0
    total_seconds = window_hours * 3600

    for event in events:
        if status in (HealthStatus.GREEN, HealthStatus.YELLOW):
            up_seconds += max(0.0, (event.timestamp - cursor).total_seconds())
        status = event.severity
        cursor = event.timestamp

    if current_status in (HealthStatus.GREEN, HealthStatus.YELLOW):
        up_seconds += max(0.0, (datetime.utcnow() - cursor).total_seconds())

    return round(min(100.0, max(0.0, (up_seconds / total_seconds) * 100)), 2)


def _build_sla(
    components: List[ComponentHealth],
    manager: Optional[ManagerStatus],
    cluster: Optional[ClusterHealth],
    agents: Optional[AgentsSummary],
) -> SlaSummary:
    component_map = {c.name: c.status for c in components}
    manager_status = manager.status if manager else HealthStatus.UNKNOWN
    api_status = component_map.get("wazuh_api", HealthStatus.UNKNOWN)
    cluster_status = cluster.status if cluster else HealthStatus.UNKNOWN

    if agents and agents.total:
        agent_connectivity = round((agents.active / agents.total) * 100, 2)
        agent_detail = f"{agents.active}/{agents.total} agentes activos ahora"
    elif agents:
        agent_connectivity = 100.0
        agent_detail = "Sin agentes registrados"
    else:
        agent_connectivity = 0.0
        agent_detail = "Sin datos de agentes"

    metrics = [
        SlaMetric(
            name="manager",
            label="Manager",
            availability=_availability_from_history("manager", manager_status, 24),
            window_hours=24,
            status=manager_status,
            detail="Disponibilidad observada últimas 24h",
        ),
        SlaMetric(
            name="wazuh_api",
            label="API",
            availability=_availability_from_history("wazuh_api", api_status, 24),
            window_hours=24,
            status=api_status,
            detail="Disponibilidad observada últimas 24h",
        ),
        SlaMetric(
            name="cluster",
            label="Cluster",
            availability=_availability_from_history("cluster", cluster_status, 168),
            window_hours=168,
            status=cluster_status,
            detail="Disponibilidad observada últimos 7d",
        ),
        SlaMetric(
            name="agents",
            label="Agentes",
            availability=agent_connectivity,
            window_hours=24,
            status=_health_status_for_percentage(agent_connectivity, yellow_at=80),
            detail=agent_detail,
        ),
    ]
    return SlaSummary(metrics=metrics)


@router.get("", response_model=OverviewHealth)
async def get_overview():
    if settings.WAZUH_MOCK:
        from app.services.mock import get_mock_overview
        data = get_mock_overview()
        return OverviewHealth(**{**data, "timestamp": datetime.utcnow()})

    results = await asyncio.gather(
        _timed("cluster", wazuh.get_cluster_health()),
        _timed("manager", wazuh.get_manager_status()),
        _timed("agents", wazuh.get_agents()),
        _timed("indexer", wazuh.get_indexer_health()),
    )

    by_name = {r["name"]: r for r in results}

    cluster = None
    manager = None
    indexer = None
    agents_summary = None
    components: List[ComponentHealth] = []
    statuses: List[HealthStatus] = []
    wazuh_api_status = HealthStatus.GREEN if any(not r["error"] for r in results[:3]) else HealthStatus.RED
    components.append(ComponentHealth(name="wazuh_api", status=wazuh_api_status))
    statuses.append(wazuh_api_status)

    if by_name["cluster"]["error"]:
        components.append(ComponentHealth(name="cluster", status=HealthStatus.UNKNOWN, details={"error": str(by_name["cluster"]["error"])}))
        statuses.append(HealthStatus.UNKNOWN)
    else:
        cluster = _parse_cluster(by_name["cluster"]["data"])
        components.append(ComponentHealth(name="cluster", status=cluster.status))
        statuses.append(cluster.status)

    if by_name["manager"]["error"]:
        components.append(ComponentHealth(name="manager", status=HealthStatus.UNKNOWN, details={"error": str(by_name["manager"]["error"])}))
        statuses.append(HealthStatus.UNKNOWN)
    else:
        manager = _parse_manager(by_name["manager"]["data"])
        components.append(ComponentHealth(name="manager", status=manager.status))
        statuses.append(manager.status)

    if by_name["agents"]["error"]:
        components.append(ComponentHealth(name="agents", status=HealthStatus.UNKNOWN, details={"error": str(by_name["agents"]["error"])}))
        statuses.append(HealthStatus.UNKNOWN)
    else:
        agents_summary = _parse_agents(by_name["agents"]["data"])
        agent_status = HealthStatus.GREEN if agents_summary.disconnected == 0 else HealthStatus.YELLOW
        components.append(ComponentHealth(name="agents", status=agent_status))
        statuses.append(agent_status)

    if by_name["indexer"]["error"]:
        components.append(ComponentHealth(name="indexer", status=HealthStatus.UNKNOWN, details={"error": str(by_name["indexer"]["error"])}))
    else:
        indexer = _parse_indexer(by_name["indexer"]["data"])
        components.append(ComponentHealth(name="indexer", status=indexer.status))

    global_status = _determine_global_status(statuses)
    health_score = _build_health_score(components, manager, cluster, indexer, agents_summary, results)
    sla = _build_sla(components, manager, cluster, agents_summary)

    overview = OverviewHealth(
        timestamp=datetime.utcnow(),
        global_status=global_status,
        cluster=cluster,
        manager=manager,
        indexer=indexer,
        agents=agents_summary,
        components=components,
        health_score=health_score,
        sla=sla,
    )

    await alerts.check_and_notify(overview.dict())

    return overview
