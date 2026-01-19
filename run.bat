@echo off
echo Starting 3D Designer Agent...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo Agent crashed or was stopped with an error.
    pause
    exit /b %errorlevel%
)
pause
