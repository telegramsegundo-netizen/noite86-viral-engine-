import pathlib
p = pathlib.Path(r"C:\Users\victo\NOITE86_FACTORY\06_READY_VIDEOS")
vids = sorted(list(p.glob("*.mp4")), key=lambda x: x.stat().st_mtime, reverse=True)
print(f"Total de vídeos no Vault: {len(vids)}")
for v in vids:
    print(f"- {v.name} ({v.stat().st_size/1024/1024:.2f} MB)")
