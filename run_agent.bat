@echo off
if not exist .env (
    echo WARNING: .env file not found. 
    echo Please copy .env.example to .env and configure your LiteLLM settings.
    echo.
)

echo 1. Setup (Install dependencies)
echo 2. Run Agent
set /p choice="Enter choice (1-2): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto run
goto end

:setup
call setup.bat
goto end

:run
call run.bat
goto end

:end
pause
