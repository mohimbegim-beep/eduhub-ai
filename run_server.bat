@echo off
echo Starting EduHub AI Server on http://localhost:8000 ...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
