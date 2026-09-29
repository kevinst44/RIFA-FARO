from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import random
import uuid
import os
from database import get_database
from config import settings

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"}
MAX_TICKETS = 300


def build_ticket_html(nombre: str, ticket_number: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Boleta #{ticket_number:03d} - Movimiento Faro</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #f0f4f8; font-family: 'Segoe UI', Arial, sans-serif; padding: 32px 16px; }}
    .container {{ max-width: 560px; margin: 0 auto; }}
    .header {{ background: linear-gradient(135deg, #1a3a2a, #2d6a4f); border-radius: 16px 16px 0 0; padding: 36px 32px; text-align: center; }}
    .header h1 {{ color: #fff; font-size: 22px; font-weight: 800; margin: 0 0 6px; letter-spacing: 0.5px; }}
    .header p {{ color: rgba(255,255,255,0.75); font-size: 13px; margin: 0; }}
    .body {{ background: #fff; padding: 36px 32px; }}
    .greeting {{ font-size: 16px; color: #374151; margin: 0 0 8px; }}
    .greeting strong {{ color: #1a3a2a; }}
    .subtitle {{ font-size: 15px; color: #6b7280; margin: 0 0 28px; line-height: 1.6; }}
    .ticket-box {{ background: linear-gradient(135deg, #1a3a2a, #2d6a4f); border-radius: 14px; padding: 28px; text-align: center; margin-bottom: 28px; }}
    .ticket-label {{ color: rgba(255,255,255,0.7); font-size: 12px; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 8px; }}
    .ticket-number {{ color: #f7c948; font-size: 52px; font-weight: 900; letter-spacing: 6px; line-height: 1; }}
    .ticket-hint {{ color: rgba(255,255,255,0.6); font-size: 11px; margin: 10px 0 0; }}
    .event-box {{ background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 22px 24px; margin-bottom: 24px; }}
    .event-title {{ color: #166534; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 16px; }}
    .event-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #d1fae5; }}
    .event-row:last-child {{ border-bottom: none; }}
    .event-label {{ color: #6b7280; font-size: 13px; }}
    .event-value {{ color: #166534; font-size: 13px; font-weight: 700; }}
    .footer {{ background: #1a3a2a; border-radius: 0 0 16px 16px; padding: 20px 32px; text-align: center; }}
    .footer p {{ color: rgba(255,255,255,0.5); font-size: 11px; margin: 0; }}
    .print-btn {{ display: block; margin: 24px auto 0; background: #2d6a4f; color: white; border: none; padding: 12px 32px; border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; }}
    @media print {{ .print-btn {{ display: none; }} }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div style="font-size:48px;margin-bottom:8px;">🏮</div>
      <h1>MOVIMIENTO FARO</h1>
      <p>YO SOY FARO</p>
    </div>
    <div class="body">
      <p class="greeting">Hola, <strong>{nombre}</strong> 👋</p>
      <p class="subtitle">Gracias por participar en la<br><strong>Integración de Amistad — Día del Movimiento Faro!</strong></p>
      <div class="ticket-box">
        <p class="ticket-label">Tu número de boleta</p>
        <div class="ticket-number">#{ticket_number:03d}</div>
        <p class="ticket-hint">¡Guarda este número — no puede repetirse!</p>
      </div>
      <div class="event-box">
        <h3 class="event-title">📅 Detalles del Evento</h3>
        <div class="event-row">
          <span class="event-label">📆 Día</span>
          <span class="event-value">{settings.EVENT_DATE}</span>
        </div>
        <div class="event-row">
          <span class="event-label">🕢 Hora</span>
          <span class="event-value">{settings.EVENT_TIME}</span>
        </div>
        <div class="event-row">
          <span class="event-label">📍 Lugar</span>
          <span class="event-value">{settings.EVENT_PLACE}</span>
        </div>
      </div>
      <p style="font-size:14px;color:#6b7280;text-align:center;line-height:1.6;">¡Te esperamos! 🎉<br><em style="color:#9ca3af;font-size:12px;">Mucha suerte con tu boleta</em></p>
      <button class="print-btn" onclick="window.print()">🖨️ Imprimir / Guardar boleta</button>
    </div>
    <div class="footer">
      <p>Movimiento Faro · {settings.RAFFLE_NAME}</p>
    </div>
  </div>
</body>
</html>"""


@router.post("/")
async def create_participant(
    nombre: str = Form(...),
    cedula: str = Form(...),
    celular: str = Form(...),
    email: str = Form(...),
    payment_image: UploadFile = File(...)
):
    if payment_image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes (JPG, PNG, WEBP)")

    db = get_database()

    # Verificar cédula duplicada
    existing = await db.participants.find_one({"cedula": cedula.strip()})
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una participación registrada con esa cédula")

    # Verificar boletas disponibles
    assigned_count = await db.participants.count_documents({"ticket_number": {"$ne": None}})
    if assigned_count >= MAX_TICKETS:
        raise HTTPException(status_code=400, detail=f"Lo sentimos, todas las {MAX_TICKETS} boletas ya fueron asignadas.")

    # Asignar número de boleta único
    used_numbers = await db.participants.distinct("ticket_number", {"ticket_number": {"$ne": None}})
    available = list(set(range(1, MAX_TICKETS + 1)) - set(used_numbers))
    if not available:
        raise HTTPException(status_code=400, detail="No quedan boletas disponibles.")
    ticket_number = random.choice(available)

    # Guardar imagen
    ext = os.path.splitext(payment_image.filename)[1] if payment_image.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join("uploads", filename)
    content = await payment_image.read()
    with open(filepath, "wb") as f:
        f.write(content)

    participant = {
        "nombre": nombre.strip(),
        "cedula": cedula.strip(),
        "celular": celular.strip(),
        "email": email.strip().lower(),
        "payment_image_url": f"/uploads/{filename}",
        "status": "pending",
        "ticket_number": ticket_number,
        "created_at": datetime.utcnow()
    }

    result = await db.participants.insert_one(participant)

    return {
        "id": str(result.inserted_id),
        "ticket_number": ticket_number,
        "message": "¡Participación registrada! Descarga tu boleta.",
        "remaining_tickets": MAX_TICKETS - assigned_count - 1
    }


@router.get("/{participant_id}/ticket", response_class=HTMLResponse)
async def download_ticket(participant_id: str):
    db = get_database()
    try:
        p = await db.participants.find_one({"_id": ObjectId(participant_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    if not p:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    if not p.get("ticket_number"):
        raise HTTPException(status_code=400, detail="Boleta aún no asignada")
    html = build_ticket_html(p["nombre"], p["ticket_number"])
    return HTMLResponse(content=html, headers={
        "Content-Disposition": f"attachment; filename=boleta-{p['ticket_number']:03d}.html"
    })


@router.get("/payment-info")
async def get_payment_info():
    return {
        "bank": settings.PAYMENT_BANK,
        "account_number": settings.PAYMENT_ACCOUNT_NUMBER,
        "account_type": settings.PAYMENT_ACCOUNT_TYPE,
        "owner": settings.PAYMENT_OWNER,
        "document": getattr(settings, "PAYMENT_DOCUMENT", ""),
        "raffle_name": settings.RAFFLE_NAME
    }


@router.get("/availability")
async def get_availability():
    db = get_database()
    assigned_count = await db.participants.count_documents({"ticket_number": {"$ne": None}})
    remaining = max(0, MAX_TICKETS - assigned_count)
    return {
        "max_tickets": MAX_TICKETS,
        "assigned": assigned_count,
        "remaining": remaining,
        "sold_out": remaining == 0,
        "percentage_taken": round((assigned_count / MAX_TICKETS) * 100, 1)
    }
