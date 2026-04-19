@echo off
echo ========================================
echo Launching AI Assistant...
echo ========================================
cd /d "%~dp0"
python start_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start with 'python'. Trying 'python3'...
    python3 start_app.py
)
pause
