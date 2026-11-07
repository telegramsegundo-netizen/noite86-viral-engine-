' NOITE 86 — Inicializador Silencioso em Segundo Plano
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\victo\teamwork_projects\gta6_ecommerce_agents"
WshShell.Run "C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.venv\Scripts\python.exe -m autonomous_engine.scheduler", 0, False
