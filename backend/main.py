from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from database import connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title="Rifa API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4201",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

from routes.auth import router as auth_router
from routes.participants import router as participants_router
from routes.admin import router as admin_router

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(participants_router, prefix="/api/participants", tags=["Participantes"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administración"])


@app.get("/")
async def root():
    return {"message": "Rifa API funcionando correctamente", "version": "1.0.0"}
