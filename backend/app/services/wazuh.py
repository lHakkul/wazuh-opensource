import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

_token: Optional[str] = None
_token_expiry: Optional[datetime] = None


async def _get_token() -> str:
    global _token, _token_expiry

    if _token and _token_expiry and datetime.utcnow() < _token_expiry:
        return _token

    async with httpx.AsyncClient(verify=settings.WAZUH_VERIFY_SSL) as client:
        resp = await client.post(
            f"{settings.WAZUH_API_URL}/security/user/authenticate",
            auth=(settings.WAZUH_API_USER, settings.WAZUH_API_PASSWORD),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        _token = data["data"]["token"]
        _token_expiry = datetime.utcnow() + timedelta(minutes=14)
        return _token


async def wazuh_get(path: str) -> dict:
    token = await _get_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(verify=settings.WAZUH_VERIFY_SSL) as client:
        resp = await client.get(
            f"{settings.WAZUH_API_URL}{path}",
            headers=headers,
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()


async def get_cluster_health() -> dict:
    try:
        # First check if cluster is enabled
        cluster_status = await wazuh_get("/cluster/status")
        enabled = cluster_status.get("data", {}).get("enabled") == "yes"
        running = cluster_status.get("data", {}).get("running") == "yes"

        if not enabled or not running:
            return {"healthcheck": {}, "nodes": {}, "enabled": False}

        nodes = await wazuh_get("/cluster/nodes")
        return {"healthcheck": {}, "nodes": nodes, "enabled": True}
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (400, 404):
            logger.info("Cluster not enabled or not available — standalone mode")
            return {"healthcheck": {}, "nodes": {}, "enabled": False}
        logger.error(f"Error fetching cluster health: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching cluster health: {e}")
        raise


async def get_agents(limit: int = 500) -> dict:
    try:
        data = await wazuh_get(f"/agents?limit={limit}&select=id,name,ip,status,version,os.name,os.platform,lastKeepAlive,manager,group")
        return data
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        raise


async def get_manager_status() -> dict:
    try:
        data = await wazuh_get("/manager/status")
        return data
    except Exception as e:
        logger.error(f"Error fetching manager status: {e}")
        raise


async def get_manager_info() -> dict:
    try:
        data = await wazuh_get("/manager/info")
        return data
    except Exception as e:
        logger.error(f"Error fetching manager info: {e}")
        raise


async def get_indexer_health() -> dict:
    try:
        data = await wazuh_get("/manager/configuration?section=indexer")
        return data
    except Exception as e:
        logger.warning(f"Could not fetch indexer health: {e}")
        return {}
