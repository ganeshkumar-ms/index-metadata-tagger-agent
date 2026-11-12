@echo off
cd /d "%~dp0"
..\..\taxora\backend\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload

