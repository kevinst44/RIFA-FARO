import logging
from config import settings

logger = logging.getLogger(__name__)


async def send_sms(phone: str, message: str) -> bool:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
        logger.warning(f"SMS no configurado. Mensaje para {phone}: {message}")
        return False

    try:
        from twilio.rest import Client

        # Formatear número para Colombia si no tiene código de país
        if not phone.startswith("+"):
            phone_clean = phone.replace(" ", "").replace("-", "")
            if phone_clean.startswith("57"):
                phone = f"+{phone_clean}"
            else:
                phone = f"+57{phone_clean}"

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        logger.info(f"SMS enviado a {phone}: SID {msg.sid}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar SMS a {phone}: {e}")
        return False
