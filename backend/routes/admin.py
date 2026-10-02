import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime
from jose import jwt, JWTError
from database import get_database
from config import settings
from services.email import send_confirmation_email

logger = logging.getLogger(__name__)


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
    created_at = p.get("created_at")
    accepted_at = p.get("accepted_at")
    pid = str(p.get("_id", ""))
    # has_image_b64 is injected by the aggregation pipeline
    has_image = p.get("has_image_b64", False)
    return {
        "id": pid,
        "nombre": p.get("nombre", ""),
        "cedula": p.get("cedula", ""),
        "celular": p.get("celular", ""),
        "email": p.get("email", ""),
        "payment_image_url": f"/api/participants/{pid}/image" if has_image else p.get("payment_image_url"),
        "status": p.get("status", "pending"),
        "ticket_number": p.get("ticket_number"),
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at) if created_at else None,
        "accepted_at": accepted_at.isoformat() if hasattr(accepted_at, "isoformat") else str(accepted_at) if accepted_at else None,
    }



@router.get("/participants")
async def get_participants(admin: str = Depends(verify_admin)):
    db = get_database()
    participants = []
    # Exclude payment_image_b64 (large base64) — inject has_image_b64 flag instead
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$addFields": {"has_image_b64": {"$cond": [{"$gt": ["$payment_image_b64", None]}, True, False]}}},
        {"$project": {"payment_image_b64": 0}},
    ]
    async for p in db.participants.aggregate(pipeline):
        try:
            participants.append(serialize_participant(p))
        except Exception as e:
            logger.error(f"Error serializing participant {p.get('_id')}: {e}")
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

    await db.participants.update_one(
        {"_id": obj_id},
        {"$set": {"status": "accepted", "accepted_at": datetime.utcnow()}}
    )

    return {
        "message": f"{participant['nombre']} marcado como asistió al evento",
        "ticket_number": participant.get("ticket_number")
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
