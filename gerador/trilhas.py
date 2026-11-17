#!/usr/bin/env python3
"""Trilhas originais do O Sino: 3 vinhetas de sino e 3 trilhas de mercado."""
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
from pathlib import Path

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
OUT = Path(__file__).parent / "wav"
OUT.mkdir(exist_ok=True)


def t_(d):
    return np.arange(int(SR * d)) / SR


def nota(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, fc, ordem=2):
    return sosfilt(butter(ordem, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, ordem=2):
    return sosfilt(butter(ordem, fc, "high", fs=SR, output="sos"), x)


def por(buf, x, inicio, ganho=1.0, pan=0.0):
    i = int(inicio * SR)
    if i >= buf.shape[1]:
        return
    x = x[: buf.shape[1] - i] * ganho
    buf[0, i:i + len(x)] += x * np.sqrt(0.5 * (1 - pan))
    buf[1, i:i + len(x)] += x * np.sqrt(0.5 * (1 + pan))


def reverb(buf, tempo=2.2, mix=0.25):
    out = np.zeros_like(buf)
    for c in range(2):
        tt = t_(tempo)
        ir = rng.standard_normal(len(tt)) * np.exp(-tt * 6.9 / tempo)
        ir = lp(ir, 6000)
        ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        out[c] = fftconvolve(buf[c], ir)[: buf.shape[1]]
    return buf * (1 - mix) + out * mix


# ---------- instrumentos ----------

PARC = [(0.5, .30, 1.6), (1.0, 1.0, 1.0), (1.183, .55, .8), (1.506, .30, .6), (2.0, .75, .5),
        (2.514, .25, .35), (2.662, .22, .3), (3.011, .18, .25), (4.166, .10, .15), (5.433, .06, .1)]


def sino(f, dur=7.0, decai=4.0, brilho=1.0):
    tt = t_(dur)
    x = np.zeros_like(tt)
    for r, a, d in PARC:
        for desv in (0.0, 0.35 * r):
            x += a * (brilho if r > 2 else 1) * np.sin(2 * np.pi * (f * r + desv) * tt + rng.uniform(0, 6.28)) * np.exp(-tt / (decai * d))
    golpe = hp(rng.standard_normal(int(0.006 * SR)), 2000) * np.linspace(1, 0, int(0.006 * SR)) * 0.6
    x[: len(golpe)] += golpe
    x *= 1 - np.exp(-tt / 0.0015)
    return x / np.max(np.abs(x))


def fm(f, dur, ind=2.5, razao=1.0, decai=0.6, ataque=0.003):
    tt = t_(dur)
    env_i = ind * np.exp(-tt / (decai * 0.5))
    x = np.sin(2 * np.pi * f * tt + env_i * np.sin(2 * np.pi * f * razao * tt))
    return x * np.exp(-tt / decai) * (1 - np.exp(-tt / ataque))


def serra(f, tt, voz=3, det=0.12):
    x = np.zeros_like(tt)
    for k in range(voz):
        ff = f * 2 ** ((k - (voz - 1) / 2) * det / 12)
        fase = rng.uniform(0, 6.28)
        for h in range(1, int(min(30, 7000 / ff)) + 1):
            x += np.sin(2 * np.pi * ff * h * tt + fase * h) / h
    return x * 0.6 / voz


def pad(notas, dur, fc=1200, ataque=1.2, solta=1.5):
    tt = t_(dur)
    x = sum(serra(nota(n), tt) for n in notas) / len(notas)
    x = lp(x, fc, 2)
    env = np.minimum(1, tt / ataque) * np.minimum(1, (dur - tt) / solta).clip(0)
    return x * env


def pluck(f, dur=0.25, fc=2500):
    tt = t_(dur)
    x = serra(f, tt, 2, 0.08) * np.exp(-tt / 0.07)
    return lp(x, fc)


def baixo(f, dur=0.22):
    tt = t_(dur)
    x = (np.sin(2 * np.pi * f * tt) + 0.4 * np.tanh(3 * np.sin(2 * np.pi * f * tt))) * np.exp(-tt / 0.12)
    return lp(x, 900)


def bumbo(dur=0.5):
    tt = t_(dur)
    fr = 45 + 90 * np.exp(-tt / 0.035)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / 0.16)


def chimbal(dur=0.05, decai=0.012):
    tt = t_(dur)
    return hp(rng.standard_normal(len(tt)), 7000) * np.exp(-tt / decai)


def tic(dur=0.03):
    tt = t_(dur)
    return hp(rng.standard_normal(len(tt)), 3000, 4) * np.exp(-tt / 0.004) + 0.5 * np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt / 0.006)


def tímpano(f, dur=1.6):
    tt = t_(dur)
    fr = f * (1 + 0.08 * np.exp(-tt / 0.05))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / 0.5)
    x += 0.3 * lp(rng.standard_normal(len(tt)), 400) * np.exp(-tt / 0.08)
    return x


def mestre(buf, nome, fade=2.0):
    tt = np.arange(buf.shape[1]) / SR
    buf = buf * np.minimum(1, (DUR - tt) / fade).clip(0)
    buf = np.tanh(1.2 * buf / (np.max(np.abs(buf)) + 1e-9)) * 0.89
    wavfile.write(OUT / f"{nome}.wav", SR, (buf.T * 32767).astype(np.int16))


def novo():
    return np.zeros((2, N))


# ---------- vinhetas ----------

def vinheta_badalada():
    b = novo()
    for k, (n, ini) in enumerate([(55, 0.0), (55, 2.4), (50, 4.8)]):  # sol, sol, ré
        por(b, sino(nota(n), 9, 4.5), ini, 0.9 - 0.15 * k, pan=(-0.2, 0.2, 0)[k])
    por(b, pad([38, 45, 50], DUR, 500, 3, 3), 0.5, 0.22)
    mestre(reverb(b, 3.0, 0.35), "v1-badalada")


def vinheta_carrilhao():
    b = novo()
    motivo = [79, 76, 74, 79, 72, 74, 76, 74]
    for i, n in enumerate(motivo):
        por(b, sino(nota(n - 12), 4, 1.6, 1.3), 0.3 + i * 0.42, 0.55, pan=np.sin(i) * 0.4)
    por(b, sino(nota(43), 10, 5), 3.9, 0.9)
    por(b, pad([48, 55, 60, 64], 11, 900, 2, 3), 3.9, 0.2)
    mestre(reverb(b, 2.6, 0.32), "v2-carrilhao")


def vinheta_pulso():
    b = novo()
    por(b, sino(nota(50), 10, 4.5), 0.0, 1.0)
    bpm = 112
    s = 60 / bpm / 4
    t0 = 1.6
    for i in range(int((DUR - t0 - 1) / s)):
        ini = t0 + i * s
        if i % 4 == 0:
            por(b, baixo(nota(38)), ini, 0.55)
        if i % 2 == 1:
            por(b, chimbal(), ini, 0.10, pan=0.3)
        if i % 8 == 6:
            por(b, fm(nota(74), 0.6, 3, 3.5, 0.25), ini, 0.10, pan=-0.3)
    por(b, pad([50, 57, 62, 65], DUR - t0, 1500, 2, 2), t0, 0.18)
    por(b, sino(nota(57), 6, 3, 1.2), 9.0, 0.4)
    mestre(reverb(b, 2.2, 0.25), "v3-pulso")


# ---------- trilhas de mercado ----------

def mercado_telejornal():
    """Abertura de jornal econômico: ostinato em semicolcheias, tímpanos e metais sintéticos."""
    b = novo()
    bpm = 124
    s = 60 / bpm / 4
    por(b, sino(nota(50), 8, 4), 0.0, 0.8)
    ost = [62, 62, 69, 62, 65, 62, 69, 67]
    acordes = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]
    t0 = 0.0
    passos = int((DUR - 1.2) / s)
    for i in range(passos):
        ini = t0 + i * s
        comp = (i // 16) % 4
        desl = [0, -4, -7, -5][comp]
        por(b, pluck(nota(ost[i % 8] + desl), 0.2, 3200), ini, 0.22, pan=0.35 if i % 2 else -0.35)
        if i % 4 == 0:
            por(b, baixo(nota(38 + desl), 0.3), ini, 0.6)
        if i % 16 == 0:
            por(b, pad(acordes[comp], 16 * s + 0.4, 2200, 0.05, 0.4), ini, 0.28)
            por(b, tímpano(nota(38 + desl)), ini, 0.5)
        if i % 4 == 2:
            por(b, chimbal(0.04), ini, 0.08, pan=0.4)
    por(b, sino(nota(50), 6, 3), passos * s, 0.7)
    mestre(reverb(b, 1.8, 0.2), "m1-telejornal")


def mercado_cotacao():
    """Ticker: relógio, arpejo que sobe e sub-grave, com sino de abertura."""
    b = novo()
    bpm = 120
    s = 60 / bpm / 4
    por(b, sino(nota(57), 8, 4), 0.0, 0.75)
    arp = [57, 60, 64, 69, 72, 69, 64, 60]
    t0 = 0.5
    for i in range(int((DUR - t0 - 1) / s)):
        ini = t0 + i * s
        por(b, tic(), ini, 0.10 if i % 4 else 0.18, pan=0.5)
        sobe = (i // 32) * 2
        if i >= 16:
            por(b, fm(nota(arp[i % 8] + sobe + 12), 0.3, 1.8, 2.0, 0.12), ini, 0.10, pan=-0.3 + 0.6 * ((i % 8) / 7))
        if i % 8 == 0:
            tt = t_(4 * s * 2)
            por(b, np.sin(2 * np.pi * nota(33 + sobe) * tt) * np.exp(-tt / 0.6), ini, 0.55)
        if i % 8 == 4 and i > 32:
            por(b, bumbo(), ini, 0.5)
    por(b, pad([45, 52, 57, 60], DUR - 2, 1000, 3, 2), 2.0, 0.16)
    mestre(reverb(b, 2.0, 0.25), "m2-cotacao")


def mercado_pregao():
    """Pregão otimista: piano elétrico, batida leve e sino no fim do compasso."""
    b = novo()
    bpm = 96
    q = 60 / bpm
    acordes = [[48, 55, 60, 64, 67], [45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [43, 50, 55, 59, 62]]
    por(b, sino(nota(60), 6, 3, 1.1), 0.0, 0.6)
    t0 = 0.6
    for c in range(int((DUR - t0) / (4 * q))):
        ac = acordes[c % 4]
        ini = t0 + c * 4 * q
        for j, ofs in enumerate([0, 1.5, 2.5]):
            for n in ac:
                por(b, fm(nota(n), 1.6, 1.2, 1.0, 0.9), ini + ofs * q + 0.008 * ac.index(n), 0.07, pan=-0.2)
        por(b, baixo(nota(ac[0] - 12), 0.6), ini, 0.55)
        por(b, baixo(nota(ac[0] - 12), 0.4), ini + 2.5 * q, 0.45)
        for k in range(4):
            por(b, bumbo(), ini + k * q, 0.45 if k % 2 == 0 else 0.0)
            if k % 2 == 1:
                tt = t_(0.2)
                por(b, hp(rng.standard_normal(len(tt)), 1500) * np.exp(-tt / 0.035), ini + k * q, 0.10)
            por(b, chimbal(), ini + k * q + q / 2, 0.08, pan=0.3)
        mel = [72, 74, 76, 79] if c % 2 == 0 else [79, 76, 74, 72]
        for k, n in enumerate(mel):
            por(b, sino(nota(n), 1.5, 0.6, 1.4), ini + (k * 0.75 + 0.5) * q, 0.12, pan=0.4)
    mestre(reverb(b, 1.6, 0.18), "m3-pregao")


if __name__ == "__main__":
    for f in (vinheta_badalada, vinheta_carrilhao, vinheta_pulso, mercado_telejornal, mercado_cotacao, mercado_pregao):
        f()
        print("ok", f.__name__)
