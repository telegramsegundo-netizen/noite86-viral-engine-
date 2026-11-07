"""Entry point para rodar o dashboard como módulo: python -m video_pipeline.dashboard_server"""
from video_pipeline.dashboard_server import app
import threading
import webbrowser

port = 8086
print("=" * 50)
print("🚀 NOITE 86 — FÁBRICA DE VÍDEOS")
print(f"   Acesse: http://localhost:{port}")
print("=" * 50)
threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
app.run(host="0.0.0.0", port=port, debug=False)
