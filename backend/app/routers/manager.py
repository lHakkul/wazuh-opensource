from fastapi import APIRouter, HTTPException
from app.services import wazuh
from app.models.schemas import ManagerStatus, HealthStatus

router = APIRouter(prefix="/api/manager", tags=["manager"])


def _parse_manager_status(raw: dict) -> ManagerStatus:
    data = raw.get("data", {}).get("affected_items", [{}])[0] if raw.get("data", {}).get("affected_items") else {}

    enabled = []
    running = []
    stopped = []

    for daemon, status in data.items():
        if status == "running":
            running.append(daemon)
            enabled.append(daemon)
        elif status == "stopped":
            stopped.append(daemon)
            enabled.append(daemon)

    if not data:
        health = HealthStatus.UNKNOWN
    elif stopped:
        health = HealthStatus.YELLOW if running else HealthStatus.RED
    else:
        health = HealthStatus.GREEN

    return ManagerStatus(
        status=health,
        enabled=enabled,
        running=running,
        stopped=stopped,
        raw=data,
    )


@router.get("/status", response_model=ManagerStatus)
async def manager_status():
    try:
        raw = await wazuh.get_manager_status()
        return _parse_manager_status(raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/info")
async def manager_info():
    try:
        data = await wazuh.get_manager_info()
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
