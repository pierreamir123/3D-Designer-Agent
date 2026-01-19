@echo off
echo Setting up 3D Designer Agent...
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to install dependencies.
    pause
    exit /b %errorlevel%
)
echo.
echo Setup complete! You can now run the agent using run.bat.
pause
