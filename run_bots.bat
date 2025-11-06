@echo off
REM Multi-Bot Runner for Windows
REM Run both bots simultaneously

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║  🚀  Multi-Bot Runner - Professional Edition 🚀          ║
echo ║                                                           ║
echo ║  ✨ APK Generator Studio                                 ║
echo ║  🔍 APK Analyzer Studio                                  ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo Starting bots...
echo.

REM Start Bot 1 in new window
start "Bot 1 - APK Generator" python m.py
echo ✅ Bot 1 - APK Generator started

timeout /t 2 /nobreak >nul

REM Start Bot 2 in new window
start "Bot 2 - APK Analyzer" python bot2.py
echo ✅ Bot 2 - APK Analyzer started

echo.
echo ✅ All bots started successfully!
echo.
echo Close this window or press Ctrl+C to stop monitoring
echo (Note: Bots will continue running in separate windows)
echo.

pause
