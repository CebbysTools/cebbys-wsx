@echo off
title NHL 27 (AnyPS5)
cd /d "%~dp0"
set ANYPS5_OUTPUT_RESOLUTION=2160p
echo Starting NHL 27 through AnyPS5. The first start compiles shaders for about 5 minutes.
echo.
eboot.exe
echo.
echo ===== The game exited with code %ERRORLEVEL% =====
echo Press Enter to close this window.
pause >nul
