@echo off
REM Standalone Agent Evaluation Script for Windows
REM Activates virtual environment and runs evaluation

echo.
echo ========================================
echo   Agent Accuracy Evaluation
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run evaluation
python evaluate_agents.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause > nul
)
