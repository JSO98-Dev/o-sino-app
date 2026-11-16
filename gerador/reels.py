#!/usr/bin/env python3
"""Reels 1080x1920 a partir de manchete-1.png e story.png.

Uso: python3 reels.py saida/   ->  saida/reels.mp4
"""
import subprocess, sys
from pathlib import Path

FUNDO = "0x151413"
FPS = 30
T1, T2, FADE = 5.0, 9.0, 0.6  # segundos: manchete, story, transição


def zoom(entrada, dur, ate):
    n = int(dur * FPS)
    return (f"{entrada}scale=2160:-2,pad=2160:3840:(ow-iw)/2:(oh-ih)/2:color={FUNDO},"
            f"zoompan=z='1+({ate}-1)*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={n}:s=1080x1920:fps={FPS},setsar=1")


def main(pasta):
    p = Path(pasta)
    man, sto, out = p / "manchete-1.png", p / "story.png", p / "reels.mp4"
    for f in (man, sto):
        if not f.exists():
            sys.exit(f"falta {f}")
    total = T1 + T2 - FADE
    filtro = (f"{zoom('[0:v]', T1, 1.06)}[a];"
              f"{zoom('[1:v]', T2, 1.05)}[b];"
              f"[a][b]xfade=transition=fade:duration={FADE}:offset={T1 - FADE},format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-i", str(man), "-i", str(sto),
           "-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo",
           "-filter_complex", filtro, "-map", "[v]", "-map", "2:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "96k", "-t", str(total), "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(out, f"{out.stat().st_size / 1e6:.1f} MB", f"{total:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "saida")
