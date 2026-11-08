import yt_dlp

ydl_opts = {"extract_flat": True, "quiet": True}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    res = ydl.extract_info("ytsearch5:gta 6 viral shorts", download=False)
    entries = res.get("entries", [])
    print(f"ytsearch entries: {len(entries)}")
    for e in entries:
        print(e.get("title"))
