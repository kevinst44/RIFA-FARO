# Sistema de Rifas

Aplicación web para gestionar rifas con formulario de participación y panel de administración.

## Tecnologías

- **Backend**: Python + FastAPI + MongoDB (Motor async)
- **Frontend**: Angular 17 + Bootstrap 5
- **SMS**: Twilio (opcional)
- **Base de datos**: MongoDB

## Estructura del proyecto

```
RIFAPROYECTO/
├── backend/         # API FastAPI
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── participants.py
│   │   └── admin.py
│   ├── services/
│   │   └── sms.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/        # App Angular
    ├── src/app/
    │   ├── components/
    │   │   ├── raffle-form/     # Formulario público
    │   │   ├── admin-panel/     # Panel de admin
    │   │   └── login-modal/     # Modal de login
    │   ├── services/
    │   └── guards/
    └── package.json
```

## Requisitos previos

- Python 3.11+
- Node.js 18+
- MongoDB (local o Atlas)
- Cuenta Twilio (opcional, para SMS)

## Instalación y arranque

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus datos reales

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

El backend estará disponible en: http://localhost:8000  
Documentación API: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

El frontend estará disponible en: http://localhost:4200

## Configuración del .env

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=rifadb
JWT_SECRET=tu-clave-secreta-aqui
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tu-password-aqui

# Twilio (opcional)
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Datos de pago para mostrar en el formulario
RAFFLE_NAME=Integración de Amistad
Día del Movimiento Faro
PAYMENT_BANK=Bancolombia
PAYMENT_ACCOUNT_NUMBER=123-456789-00
PAYMENT_ACCOUNT_TYPE=Cuenta de Ahorros
PAYMENT_OWNER=Nombre del Organizador
PAYMENT_DOCUMENT=900.123.456-7
```

## Flujo de uso

### Participante
1. Accede a http://localhost:4200
2. Completa el formulario: nombre, cédula, celular
3. Indica si ya sabe dónde pagar (si dice NO, ve los datos de pago)
4. Adjunta la imagen del comprobante de pago
5. Envía el formulario

### Administrador
1. En la esquina superior izquierda, haz clic en el ícono del **faro** (lighthouse)
2. Ingresa usuario y contraseña
3. En el panel admin puedes ver todas las participaciones con sus fotos
4. Haz clic en **"Ver Imagen"** para ver el comprobante a pantalla completa
5. Haz clic en **"Aceptar"** para:
   - Asignar número de boleta automáticamente
   - Enviar SMS al participante con el número de boleta

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/auth/login | Login administrador |
| GET | /api/participants/payment-info | Datos de pago (público) |
| POST | /api/participants/ | Registrar participante |
| GET | /api/admin/participants | Listar participantes (admin) |
| POST | /api/admin/participants/{id}/accept | Aceptar y enviar SMS |
| POST | /api/admin/participants/{id}/reject | Rechazar participante |
| GET | /api/admin/stats | Estadísticas (admin) |
