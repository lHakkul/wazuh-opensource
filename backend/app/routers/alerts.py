from fastapi import APIRouter, HTTPException
from app.services import alerts
from app.config import settings
from app.models.schemas import AlertConfig

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/config", response_model=AlertConfig)
async def get_alert_config():
    return AlertConfig(
        telegram_enabled=bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID),
        slack_enabled=bool(settings.SLACK_WEBHOOK_URL),
    )


@router.post("/test/telegram")
async def test_telegram():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram no configurado")
    await alerts.send_telegram("✅ <b>Wazuh Monitor</b>\nPrueba de notificación Telegram exitosa.")
    return {"message": "Notificación enviada"}


@router.post("/test/slack")
async def test_slack():
    if not settings.SLACK_WEBHOOK_URL:
        raise HTTPException(status_code=400, detail="Slack no configurado")
    await alerts.send_slack("✅ *Wazuh Monitor*\nPrueba de notificación Slack exitosa.")
    return {"message": "Notificación enviada"}
