@echo off
setlocal

set "PY_CMD="

:: Prefer Python Launcher with explicit 3.11
where py >nul 2>nul
if %errorlevel%==0 (
    py -3.11 --version >nul 2>nul
    if %errorlevel%==0 (
        set "PY_CMD=py -3.11"
    )
)

:: Fallback: python on PATH already 3.11
if not defined PY_CMD (
    python --version 2>nul | findstr /C:"Python 3.11" >nul
    if %errorlevel%==0 (
        set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo ERROR: Python 3.11 is required for this project.
    echo Install Python 3.11 and ensure one of these works:
    echo   py -3.11 --version
    echo   python --version  ^(returns Python 3.11.x^)
    pause
    exit /b 1
)

:: Create venv if missing
if not exist venv\Scripts\python.exe (
    %PY_CMD% -m venv venv
    call venv\Scripts\pip install -r requirements.txt
)

:: Verify existing venv is Python 3.11
venv\Scripts\python --version 2>nul | findstr /C:"Python 3.11" >nul
if errorlevel 1 (
    echo ERROR: Existing venv is not Python 3.11.
    echo Delete the venv folder and rerun start.bat to recreate it with Python 3.11.
    pause
    exit /b 1
)

call venv\Scripts\streamlit run app.py --server.headless true --server.port 8501
