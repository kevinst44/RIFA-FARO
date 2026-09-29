from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import os
from database import get_database
from config import settings
from services.email_verify import create_verification_code, check_verification_code, is_email_verified
from services.email import send_verification_email

router = APIRouter()


class EmailRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    code: str

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"}
MAX_TICKETS = 300


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
        raise HTTPException(
            status_code=400,
            detail="Ya existe una participación registrada con esa cédula"
        )

    # Verificar que aún hay boletas disponibles
    accepted_count = await db.participants.count_documents({"status": "accepted"})
    if accepted_count >= MAX_TICKETS:
        raise HTTPException(
            status_code=400,
            detail=f"Lo sentimos, todas las {MAX_TICKETS} boletas ya han sido asignadas."
        )

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
        "ticket_number": None,
        "created_at": datetime.utcnow()
    }

    result = await db.participants.insert_one(participant)

    remaining = MAX_TICKETS - accepted_count
    return {
        "id": str(result.inserted_id),
        "message": "¡Participación registrada exitosamente! Pronto verificaremos tu pago.",
        "remaining_tickets": remaining
    }


@router.post("/send-verification")
async def send_email_verification(data: EmailRequest):
    email = data.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Correo inválido")

    code = await create_verification_code(email)
    sent = await send_verification_email(email, code)

    if not sent:
        raise HTTPException(status_code=500, detail="No se pudo enviar el código. Verifica tu correo e intenta de nuevo.")

    return {"message": "Código enviado. Revisa tu bandeja de entrada (y spam)."}


@router.post("/verify-code")
async def verify_email_code(data: VerifyRequest):
    email = data.email.strip().lower()
    ok = await check_verification_code(email, data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Código incorrecto o expirado. Solicita uno nuevo.")
    return {"verified": True}


@router.get("/payment-info")
async def get_payment_info():
    return {
        "bank": settings.PAYMENT_BANK,
        "account_number": settings.PAYMENT_ACCOUNT_NUMBER,
        "account_type": settings.PAYMENT_ACCOUNT_TYPE,
        "owner": settings.PAYMENT_OWNER,
        "document": settings.PAYMENT_DOCUMENT,
        "raffle_name": settings.RAFFLE_NAME
    }


@router.get("/availability")
async def get_availability():
    db = get_database()
    accepted_count = await db.participants.count_documents({"status": "accepted"})
    remaining = max(0, MAX_TICKETS - accepted_count)
    return {
        "max_tickets": MAX_TICKETS,
        "assigned": accepted_count,
        "remaining": remaining,
        "sold_out": remaining == 0,
        "percentage_taken": round((accepted_count / MAX_TICKETS) * 100, 1)
    }
