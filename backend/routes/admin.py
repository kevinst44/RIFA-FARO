import random
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime
from jose import jwt, JWTError
from database import get_database
from config import settings
from services.sms import send_sms
from services.email import send_confirmation_email


class ParticipantUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[str] = None

router = APIRouter()
security = HTTPBearer()

MAX_TICKETS = 300


async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def serialize_participant(p: dict) -> dict:
    return {
        "id": str(p["_id"]),
        "nombre": p["nombre"],
        "cedula": p["cedula"],
        "celular": p["celular"],
        "email": p.get("email", ""),
        "payment_image_url": f"/api/participants/{str(p['_id'])}/image" if p.get("payment_image_b64") else p.get("payment_image_url"),
        "status": p["status"],
        "ticket_number": p.get("ticket_number"),
        "created_at": p["created_at"].isoformat() if p.get("created_at") else None,
        "accepted_at": p["accepted_at"].isoformat() if p.get("accepted_at") else None,
    }


async def get_available_ticket_number(db) -> int:
    """Obtiene un número de boleta aleatorio único entre 1 y MAX_TICKETS."""
    # Obtener todos los números ya usados
    used_numbers = set()
    async for p in db.participants.find(
        {"status": "accepted", "ticket_number": {"$ne": None}},
        {"ticket_number": 1}
    ):
        if p.get("ticket_number"):
            used_numbers.add(p["ticket_number"])

    if len(used_numbers) >= MAX_TICKETS:
        raise HTTPException(
            status_code=400,
            detail=f"Se ha alcanzado el límite de {MAX_TICKETS} boletas. No hay más números disponibles."
        )

    # Números disponibles del 1 al MAX_TICKETS
    available = list(set(range(1, MAX_TICKETS + 1)) - used_numbers)
    return random.choice(available)


@router.get("/participants")
async def get_participants(admin: str = Depends(verify_admin)):
    db = get_database()
    participants = []
    async for p in db.participants.find().sort("created_at", -1):
        participants.append(serialize_participant(p))
    return participants


@router.post("/participants/{participant_id}/accept")
async def accept_participant(participant_id: str, admin: str = Depends(verify_admin)):
    db = get_database()

    try:
        obj_id = ObjectId(participant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de participante inválido")

    participant = await db.participants.find_one({"_id": obj_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    if participant["status"] == "accepted":
        raise HTTPException(status_code=400, detail="Este participante ya fue aceptado")

    # Obtener número aleatorio único (lanza error si no hay disponibles)
    ticket_number = await get_available_ticket_number(db)

    await db.participants.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "status": "accepted",
                "ticket_number": ticket_number,
                "accepted_at": datetime.utcnow()
            }
        }
    )

    # Calcular boletas restantes para informar
    remaining = MAX_TICKETS - (await db.participants.count_documents({"status": "accepted"}))

    # SMS de confirmación
    sms_message = (
        f"Gracias por participar en la\n"
        f"Integracion de Amistad\n"
        f"Dia del Movimiento Faro!!\n\n"
        f"Dia: Sabado 3 de Octubre de 2026\n"
        f"Hora: 7:30PM\n"
        f"Lugar: Salon de eventos Parque del Amor\n\n"
        f"Numero de boleta: #{ticket_number:03d}"
    )

    sms_sent = await send_sms(participant["celular"], sms_message)

    # Enviar email de confirmación
    email_sent = False
    if participant.get("email"):
        email_sent = await send_confirmation_email(
            to_email=participant["email"],
            nombre=participant["nombre"],
            ticket_number=ticket_number
        )

    return {
        "message": "Participante aceptado exitosamente",
        "ticket_number": ticket_number,
        "sms_sent": sms_sent,
        "email_sent": email_sent,
        "remaining_tickets": remaining
    }


@router.post("/participants/{participant_id}/reject")
async def reject_participant(participant_id: str, admin: str = Depends(verify_admin)):
    db = get_database()

    try:
        obj_id = ObjectId(participant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    participant = await db.participants.find_one({"_id": obj_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    await db.participants.update_one(
        {"_id": obj_id},
        {"$set": {"status": "rejected"}}
    )

    return {"message": "Participante rechazado"}


@router.put("/participants/{participant_id}")
async def update_participant(participant_id: str, data: ParticipantUpdate, admin: str = Depends(verify_admin)):
    db = get_database()
    try:
        obj_id = ObjectId(participant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    participant = await db.participants.find_one({"_id": obj_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    update_fields = {}
    if data.nombre and data.nombre.strip():
        update_fields["nombre"] = data.nombre.strip()
    if data.cedula and data.cedula.strip():
        # Verificar que la nueva cédula no esté en uso por otro participante
        existing = await db.participants.find_one({"cedula": data.cedula.strip(), "_id": {"$ne": obj_id}})
        if existing:
            raise HTTPException(status_code=400, detail="Esa cédula ya está registrada por otro participante")
        update_fields["cedula"] = data.cedula.strip()
    if data.celular and data.celular.strip():
        update_fields["celular"] = data.celular.strip()
    if data.email and data.email.strip():
        update_fields["email"] = data.email.strip().lower()

    if not update_fields:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    await db.participants.update_one({"_id": obj_id}, {"$set": update_fields})
    updated = await db.participants.find_one({"_id": obj_id})
    return serialize_participant(updated)


@router.post("/participants/{participant_id}/resend-email")
async def resend_email(participant_id: str, admin: str = Depends(verify_admin)):
    db = get_database()
    try:
        obj_id = ObjectId(participant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    participant = await db.participants.find_one({"_id": obj_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    if participant["status"] != "accepted":
        raise HTTPException(status_code=400, detail="Solo se puede reenviar el correo a participantes aceptados")
    if not participant.get("email"):
        raise HTTPException(status_code=400, detail="Este participante no tiene correo registrado")
    if not participant.get("ticket_number"):
        raise HTTPException(status_code=400, detail="Este participante no tiene boleta asignada")

    email_sent = await send_confirmation_email(
        to_email=participant["email"],
        nombre=participant["nombre"],
        ticket_number=participant["ticket_number"]
    )

    if not email_sent:
        raise HTTPException(status_code=500, detail="No se pudo enviar el correo. Verifica la configuración SMTP.")

    return {"message": f"Correo reenviado a {participant['email']} — Boleta #{participant['ticket_number']:03d}"}


@router.get("/stats")
async def get_stats(admin: str = Depends(verify_admin)):
    db = get_database()
    total = await db.participants.count_documents({})
    pending = await db.participants.count_documents({"status": "pending"})
    accepted = await db.participants.count_documents({"status": "accepted"})
    rejected = await db.participants.count_documents({"status": "rejected"})
    remaining_tickets = MAX_TICKETS - accepted

    return {
        "total": total,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected,
        "max_tickets": MAX_TICKETS,
        "remaining_tickets": max(0, remaining_tickets)
    }
