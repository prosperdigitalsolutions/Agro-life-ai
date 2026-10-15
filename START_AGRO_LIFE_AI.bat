@echo off
title AGRO LIFE-AI Application
color 0A

cd /d "C:\Users\PROSPER\Documents\PROSPER WORKSPACE\03 MINI PROJECTS\AGRO LIFE-AI"

if not exist "app.py" (
    echo ERROR: AGRO LIFE-AI application files were not found.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: The project's virtual environment was not found.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo        AGRO LIFE-AI
echo   Agricultural Intelligence Platform
echo ==========================================
echo.
echo Starting the application...
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo AGRO LIFE-AI has stopped.
pause
