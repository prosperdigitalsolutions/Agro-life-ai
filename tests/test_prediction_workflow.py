```bat
@echo off
title AGRO LIFE-AI Application
color 0A

cd /d "C:\Users\PROSPER\Documents\PROSPER WORKSPACE\03 MINI PROJECTS\AGRO LIFE-AI"

if not exist "app.py" (
    echo ERROR: AGRO LIFE-AI application files were not found.
    echo Please check the project folder.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    call ".venv\Scripts\activate.bat"
) else (
    echo ERROR: The project's virtual environment was not found.
    echo Please check that the .venv folder exists.
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
echo Please wait for Streamlit to start.
echo.

python -m streamlit run app.py

echo.
echo AGRO LIFE-AI has stopped.
pause
```
