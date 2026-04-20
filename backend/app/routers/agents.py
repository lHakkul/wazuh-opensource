from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.services import wazuh
from app.models.schemas import AgentsSummary, Agent, AgentStatus, HealthStatus

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _parse_agents(raw: dict) -> AgentsSummary:
    items = raw.get("data", {}).get("affected_items", [])

    agents = []
    for item in items:
        os_info = item.get("os", {}) or {}
        status_str = item.get("status", "never_connected").lower().replace(" ", "_")
        try:
            status = AgentStatus(status_str)
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


@router.get("", response_model=AgentsSummary)
async def list_agents(limit: int = Query(500, ge=1, le=1000)):
    if settings.WAZUH_MOCK:
        from app.services.mock import get_mock_agents, MOCK_OVERVIEW
        agents_list = [Agent(**a) for a in get_mock_agents()]
        mo = MOCK_OVERVIEW["agents"]
        return AgentsSummary(
            total=mo["total"], active=mo["active"], disconnected=mo["disconnected"],
            pending=mo["pending"], never_connected=mo["never_connected"], agents=agents_list,
        )
    try:
        raw = await wazuh.get_agents(limit=limit)
        return _parse_agents(raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/summary")
async def agents_summary():
    try:
        raw = await wazuh.get_agents()
        summary = _parse_agents(raw)
        return {
            "total": summary.total,
            "active": summary.active,
            "disconnected": summary.disconnected,
            "pending": summary.pending,
            "never_connected": summary.never_connected,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
