from fastapi import APIRouter, HTTPException
from app.services import wazuh
from app.models.schemas import ClusterHealth, ClusterNode, HealthStatus

router = APIRouter(prefix="/api/cluster", tags=["cluster"])


def _parse_cluster(raw: dict) -> ClusterHealth:
    enabled = raw.get("enabled", True)

    if not enabled:
        return ClusterHealth(status=HealthStatus.GREEN, enabled=False, running=False, nodes=[])

    nodes_raw = raw.get("nodes", {}).get("data", {}).get("affected_items", [])
    nodes = []
    for n in nodes_raw:
        nodes.append(ClusterNode(
            name=n.get("name", ""),
            type=n.get("type", ""),
            version=n.get("version", ""),
            address=n.get("ip", ""),
            status=n.get("status", ""),
        ))

    active_nodes = [n for n in nodes if n.status == "connected"]

    if not nodes:
        status = HealthStatus.GREEN
    elif len(active_nodes) == len(nodes):
        status = HealthStatus.GREEN
    elif len(active_nodes) > 0:
        status = HealthStatus.YELLOW
    else:
        status = HealthStatus.RED

    return ClusterHealth(
        status=status,
        enabled=True,
        running=len(active_nodes) > 0,
        nodes=nodes,
    )


@router.get("/health", response_model=ClusterHealth)
async def cluster_health():
    try:
        raw = await wazuh.get_cluster_health()
        return _parse_cluster(raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/nodes")
async def cluster_nodes():
    try:
        data = await wazuh.wazuh_get("/cluster/nodes")
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
