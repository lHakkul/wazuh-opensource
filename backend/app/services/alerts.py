import httpx
import logging
from app.config import settings
from app.models.schemas import HealthStatus

logger = logging.getLogger(__name__)

_previous_states: dict = {}


async def send_telegram(message: str):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            }, timeout=10)
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")


async def send_slack(message: str):
    if not settings.SLACK_WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")


async def _maybe_notify(component: str, status: HealthStatus, message: str):
    prev = _previous_states.get(component)
    if prev == status:
        return
    _previous_states[component] = status

    if status in (HealthStatus.RED, HealthStatus.UNKNOWN):
        icon = "🔴"
    elif status == HealthStatus.YELLOW:
        icon = "⚠️"
    elif status == HealthStatus.GREEN and prev in (HealthStatus.RED, HealthStatus.YELLOW, HealthStatus.UNKNOWN):
        icon = "✅"
    else:
        return

    tg_text = f"{icon} <b>Wazuh Pulse Monitor - {component}</b>\nEstado: <b>{status.upper()}</b>\n{message}"
    sl_text = f"{icon} *Wazuh Pulse Monitor - {component}*\nEstado: *{status.upper()}*\n{message}"
    await send_telegram(tg_text)
    await send_slack(sl_text)


async def check_and_notify(overview: dict):
    from app.services import history as hist

    # Use the pre-computed components list from the overview
    components = overview.get("components", [])
    for comp in components:
        name = comp.get("name", "")
        status_str = comp.get("status", "unknown")
        try:
            status = HealthStatus(status_str)
        except ValueError:
            status = HealthStatus.UNKNOWN

        prev = _previous_states.get(name)
        if prev != status:
            msg = f"El componente {name} cambió a {status.upper()}"
            await _maybe_notify(name, status, msg)
            hist.add_event("status_change", status, name, msg, details=comp)

    # Extra check: alert when agents disconnect
    agents = overview.get("agents") or {}
    disconnected = agents.get("disconnected", 0)
    prev_dc = _previous_states.get("_agents_disconnected", 0)
    if disconnected != prev_dc and disconnected > 0:
        _previous_states["_agents_disconnected"] = disconnected
        msg = f"{disconnected} agente(s) desconectado(s) detectados"
        await send_telegram(f"⚠️ <b>Wazuh Pulse Monitor - Agentes</b>\n{msg}")
        await send_slack(f"⚠️ *Wazuh Pulse Monitor - Agentes*\n{msg}")
        hist.add_event("agents_disconnected", HealthStatus.YELLOW, "agents", msg,
                       details={"disconnected": disconnected})
    elif disconnected == 0 and prev_dc > 0:
        _previous_states["_agents_disconnected"] = 0
