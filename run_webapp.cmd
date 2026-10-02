@echo off
REM Quick launcher for the Streamlit web app

echo.
echo ========================================
echo   Agentic Code Reviewer - Web Interface
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Check if streamlit is installed
py -c "import streamlit" 2>NUL
if errorlevel 1 (
    echo Streamlit not found. Installing...
    pip install streamlit
)

REM Run the app
echo.
echo Starting web app...
echo Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
