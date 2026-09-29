@echo off
echo ============================================
echo   INSTALANDO DEPENDENCIAS DEL BACKEND...
echo ============================================
pip install -r requirements.txt

echo.
echo ============================================
echo   ARRANCANDO SERVIDOR...
echo ============================================
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
