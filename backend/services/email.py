import logging
from config import settings

logger = logging.getLogger(__name__)


def build_email_html(nombre: str, ticket_number: int) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tu Boleta - Movimiento Faro</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a3a2a,#2d6a4f);border-radius:16px 16px 0 0;padding:36px 32px;text-align:center;">
              <div style="font-size:48px;margin-bottom:8px;">🏮</div>
              <h1 style="color:#ffffff;font-size:22px;font-weight:800;margin:0 0 6px;letter-spacing:0.5px;">
                MOVIMIENTO FARO
              </h1>
              <p style="color:rgba(255,255,255,0.75);font-size:13px;margin:0;">
                YO SOY FARO
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:36px 32px;">

              <p style="font-size:16px;color:#374151;margin:0 0 8px;">
                Hola, <strong style="color:#1a3a2a;">{nombre}</strong> 👋
              </p>
              <p style="font-size:15px;color:#6b7280;margin:0 0 28px;line-height:1.6;">
                Gracias por participar en la
                <strong style="color:#2d6a4f;">Integración de Amistad<br>Día del Movimiento Faro!!</strong>
              </p>

              <!-- Ticket number highlight -->
              <div style="background:linear-gradient(135deg,#1a3a2a,#2d6a4f);border-radius:14px;padding:28px;text-align:center;margin-bottom:28px;">
                <p style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 8px;">Tu número de boleta</p>
                <div style="color:#f7c948;font-size:52px;font-weight:900;letter-spacing:6px;line-height:1;">
                  #{ticket_number:03d}
                </div>
                <p style="color:rgba(255,255,255,0.6);font-size:11px;margin:10px 0 0;">
                  ¡Guarda este número — no puede repetirse!
                </p>
              </div>

              <!-- Event details -->
              <div style="background:#f0fdf4;border:2px solid #86efac;border-radius:12px;padding:22px 24px;margin-bottom:24px;">
                <h3 style="color:#166534;font-size:14px;text-transform:uppercase;letter-spacing:1px;margin:0 0 16px;">
                  📅 Detalles del Evento
                </h3>
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="padding:6px 0;border-bottom:1px solid #d1fae5;">
                      <span style="color:#6b7280;font-size:13px;">📆 Día</span>
                    </td>
                    <td style="padding:6px 0;border-bottom:1px solid #d1fae5;text-align:right;">
                      <strong style="color:#166534;font-size:13px;">{settings.EVENT_DATE}</strong>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:6px 0;border-bottom:1px solid #d1fae5;">
                      <span style="color:#6b7280;font-size:13px;">🕢 Hora</span>
                    </td>
                    <td style="padding:6px 0;border-bottom:1px solid #d1fae5;text-align:right;">
                      <strong style="color:#166534;font-size:13px;">{settings.EVENT_TIME}</strong>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:6px 0;">
                      <span style="color:#6b7280;font-size:13px;">📍 Lugar</span>
                    </td>
                    <td style="padding:6px 0;text-align:right;">
                      <strong style="color:#166534;font-size:13px;">{settings.EVENT_PLACE}</strong>
                    </td>
                  </tr>
                </table>
              </div>

              <p style="font-size:14px;color:#6b7280;text-align:center;margin:0;line-height:1.6;">
                ¡Te esperamos! 🎉<br>
                <em style="color:#9ca3af;font-size:12px;">Mucha suerte con tu boleta</em>
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#1a3a2a;border-radius:0 0 16px 16px;padding:20px 32px;text-align:center;">
              <p style="color:rgba(255,255,255,0.5);font-size:11px;margin:0;">
                Movimiento Faro · {settings.RAFFLE_NAME}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_verification_email(to_email: str, code: str) -> bool:
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD or not settings.MAIL_FROM:
        logger.warning(f"Email no configurado. Código para {to_email}: {code}")
        return False

    html = f"""
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
    <tr><td align="center">
      <table width="100%" style="max-width:480px;">
        <tr><td style="background:linear-gradient(135deg,#1a3a2a,#2d6a4f);border-radius:16px 16px 0 0;padding:28px;text-align:center;">
          <h1 style="color:#fff;font-size:20px;margin:0;">🏮 MOVIMIENTO FARO</h1>
        </td></tr>
        <tr><td style="background:#fff;padding:36px 32px;text-align:center;">
          <p style="color:#374151;font-size:15px;margin:0 0 24px;">Tu código de verificación es:</p>
          <div style="background:#1a3a2a;border-radius:12px;padding:24px;display:inline-block;margin-bottom:24px;">
            <span style="color:#f7c948;font-size:42px;font-weight:900;letter-spacing:10px;">{code}</span>
          </div>
          <p style="color:#9ca3af;font-size:13px;margin:0;">Este código expira en <strong>10 minutos</strong>.<br>Si no solicitaste esto, ignora este mensaje.</p>
        </td></tr>
        <tr><td style="background:#1a3a2a;border-radius:0 0 16px 16px;padding:16px;text-align:center;">
          <p style="color:rgba(255,255,255,0.5);font-size:11px;margin:0;">Movimiento Faro · Verificación de correo</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>
"""

    try:
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        message = MessageSchema(
            subject="🔐 Tu código de verificación — Movimiento Faro",
            recipients=[to_email],
            body=html,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Código de verificación enviado a {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando código a {to_email}: {e}")
        return False


async def send_confirmation_email(to_email: str, nombre: str, ticket_number: int) -> bool:
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD or not settings.MAIL_FROM:
        logger.warning(
            f"Email no configurado. Enviaría a {to_email}: boleta #{ticket_number:03d}"
        )
        return False

    try:
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        message = MessageSchema(
            subject=f"🎟️ Tu boleta #{ticket_number:03d} — Integración de Amistad Faro",
            recipients=[to_email],
            body=build_email_html(nombre, ticket_number),
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email enviado a {to_email} — boleta #{ticket_number:03d}")
        return True

    except Exception as e:
        logger.error(f"Error enviando email a {to_email}: {e}")
        return False
