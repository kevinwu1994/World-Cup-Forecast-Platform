@echo off

cd /d "%~dp0"

echo.
echo ========================================
echo   WORLD CUP FORECAST DASHBOARD
echo   PORT: 8503
echo ========================================
echo.

start http://localhost:8503

streamlit run app.py --server.port 8503 --server.headless true

pause