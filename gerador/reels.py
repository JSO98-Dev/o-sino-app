#!/usr/bin/env python3
"""Vídeos 1080x1920 com a trilha do O Sino.

Uso: python3 reels.py saida/
  saida/story.png                      -> saida/story.mp4 (10 s)
  saida/manchete-1.png + story.png     -> saida/reels.mp4 (13 s)
"""
import subprocess, sys, urllib.request
from pathlib import Path

FUNDO = "0x151413"
FPS = 30
T1, T2, FADE = 5.0, 9.0, 0.6  # reels: manchete, story, transição
TS = 10.0                       # story
TRILHA = Path(__file__).parent / "trilha.m4a"
RAW = "https://raw.githubusercontent.com/JSO98-Dev/o-sino-app/main/gerador/trilha.m4a"


def trilha():
    if not TRILHA.exists():
        try:
            urllib.request.urlretrieve(RAW, TRILHA)
        except Exception as e:
            print("sem trilha:", e)
    return TRILHA if TRILHA.exists() else None


def zoom(entrada, dur, ate):
    n = int(dur * FPS)
    return (f"{entrada}scale=2160:-2,pad=2160:3840:(ow-iw)/2:(oh-ih)/2:color={FUNDO},"
            f"zoompan=z='1+({ate}-1)*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={n}:s=1080x1920:fps={FPS},setsar=1")


def video(imagens, filtro_v, total, out):
    tr = trilha()
    audio = ["-i", str(tr)] if tr else ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo"]
    fa = f"[{len(imagens)}:a]atrim=0:{total},afade=t=out:st={total - 1.2}:d=1.2[a]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for im in imagens:
        cmd += ["-i", str(im)]
    cmd += audio + ["-filter_complex", f"{filtro_v};{fa}", "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-t", str(total),
                    "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(out, f"{out.stat().st_size / 1e6:.1f} MB", f"{total:.1f} s")


def main(pasta):
    p = Path(pasta)
    man, sto = p / "manchete-1.png", p / "story.png"
    if not sto.exists():
        sys.exit(f"falta {sto}")
    video([sto], f"{zoom('[0:v]', TS, 1.05)},format=yuv420p[v]", TS, p / "story.mp4")
    if man.exists():
        total = T1 + T2 - FADE
        fv = (f"{zoom('[0:v]', T1, 1.06)}[m];"
              f"{zoom('[1:v]', T2, 1.05)}[s];"
              f"[m][s]xfade=transition=fade:duration={FADE}:offset={T1 - FADE},format=yuv420p[v]")
        video([man, sto], fv, total, p / "reels.mp4")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "saida")
