@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   NOITE 86 - FABRICA INTELIGENTE DE VIDEOS
echo   Iniciando painel no navegador...
echo ==========================================
echo.
cd /d "C:\Users\victo\teamwork_projects\gta6_ecommerce_agents"
"C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.venv\Scripts\python.exe" -m video_pipeline.dashboard_server
pause
