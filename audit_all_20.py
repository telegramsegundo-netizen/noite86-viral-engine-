import sys
from pathlib import Path
from autonomous_engine.audio_taskforce import AudioQualityTaskforce

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ready_dir = Path(r"C:\Users\victo\NOITE86_FACTORY\06_READY_VIDEOS")
taskforce = AudioQualityTaskforce()

videos = sorted([p for p in ready_dir.glob("gta6_*.mp4")], key=lambda p: p.name)
print(f"=== RELATÓRIO DE AUDITORIA FINAL DA SAFRA 20 (AGENTE 15) ===")
print(f"Total de cortes temáticos avaliados: {len(videos)}\n")

all_passed = True
for idx, v in enumerate(videos, start=1):
    rep = taskforce.audit_audio_integrity(v)
    passed_str = "APROVADO" if rep.passed else "FALHA"
    if not rep.passed:
        all_passed = False
    print(f"[{idx:02d}/20] {v.name} -> {passed_str}")
    print(f"       Loudness: {rep.integrated_lufs} LUFS | Peak: {rep.true_peak_db} dBFS | Score: {rep.score}/100")

print(f"\nResultado Geral: {'100% APROVADO COM EXCELÊNCIA' if all_passed else 'Existem pendências'}")
