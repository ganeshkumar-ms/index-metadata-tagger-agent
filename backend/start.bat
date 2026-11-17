@echo off
cd /d "%~dp0"
..\..\taxora-taxonomy-agent\backend\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload

