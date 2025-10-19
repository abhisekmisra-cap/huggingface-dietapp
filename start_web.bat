@echo off
echo ===============================================
echo   Diet Plan Generator - Web Interface
echo ===============================================
echo.
echo Starting the web application...
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    .venv\Scripts\python.exe app.py
) else (
    echo Using system Python...
    python app.py
)

pause