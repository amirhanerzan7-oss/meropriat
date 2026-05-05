@echo off
title Amirkhan Event Platform Server
color 0A
echo.
echo ========================================
echo    Amirkhan Event Platform
echo    Starting Server...
echo ========================================
echo.
echo Server will be available at:
echo    http://127.0.0.1:5000
echo    http://192.168.5.101:5000
echo.
echo Press CTRL+C to stop server
echo ========================================
echo.

cd /d "%~dp0"
python app.py

pause
