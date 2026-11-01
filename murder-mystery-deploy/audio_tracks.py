"""
Original noir soundtrack for the Murder Mystery app.

Five loopable, royalty-free tracks are synthesised with numpy and written as
16-bit mono WAV files next to the app. Nothing is downloaded, so the soundtrack
works completely offline and adds no licensing headaches.

Run ``python audio_tracks.py`` to (re)generate every track.
"""
from __future__ import annotations

import wave
from pathlib import Path
from typing import Dict, List

import numpy as np

SR = 22050
DURATION = 32.0
AUDIO_DIR = Path(__file__).resolve().parent / "audio"

TRACKS: List[Dict[str, str]] = [
    {
        "id": "midnight",
        "title": "Midnight Manor",
        "icon": "🕯️",
        "file": "midnight_manor.wav",
        "description": "A low drone, a heartbeat, and a clock somewhere upstairs.",
    },
    {
        "id": "rain",
        "title": "Rain on the Case File",
        "icon": "🌧️",
        "file": "rain_on_the_case_file.wav",
        "description": "Rain against the windows while the evidence is laid out.",
    },
    {
        "id": "shadows",
        "title": "Shadows in the Hall",
        "icon": "🌒",
        "file": "shadows_in_the_hall.wav",
        "description": "A detuned string cluster and a music box down the corridor.",
    },
    {
        "id": "interrogation",
        "title": "The Interrogation",
        "icon": "🔦",
        "file": "the_interrogation.wav",
        "description": "A tense pulse, brushed hats and a dissonant held note.",
    },
    {
        "id": "closed",
        "title": "Case Closed",
        "icon": "🥃",
        "file": "case_closed.wav",
        "description": "The slower, warmer theme for the final confession.",
    },
]

TRACK_BY_ID = {t["id"]: t for t in TRACKS}
STING_FILE = "case_solved_sting.wav"


# ------------------------------------------------------------------ helpers
def _n(duration: float) -> int:
    return int(duration * SR)


def _time(duration: float) -> np.ndarray:
    return np.arange(_n(duration)) / SR


def _mix_into(buffer: np.ndarray, signal: np.ndarray, start: float) -> None:
    i = int(start * SR)
    if i >= len(buffer):
        return
    j = min(len(buffer), i + len(signal))
    buffer[i:j] += signal[: j - i]


def _pad(freqs, duration, amp=0.2, rng=None, attack=1.6, release=2.4):
    """Slow, detuned analogue-style pad."""
    n = _n(duration)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        for detune in (-0.17, 0.0, 0.17):
            phase = rng.uniform(0, 2 * np.pi) if rng is not None else 0.0
            sig += np.sin(2 * np.pi * (f + detune) * t + phase)
    sig /= max(1, len(freqs) * 3)
    env = np.minimum(1.0, t / attack) * np.clip((duration - t) / release, 0, 1)
    tremolo = 0.82 + 0.18 * np.sin(2 * np.pi * 0.07 * t)
    return amp * sig * env * tremolo


def _bell(freq, duration=2.6, amp=0.2, rng=None):
    """Music-box / distant bell with inharmonic partials."""
    n = _n(duration)
    t = np.arange(n) / SR
    env = np.exp(-t * 2.1)
    partials = ((1.0, 1.0), (2.01, 0.42), (3.03, 0.22), (4.18, 0.1))
    sig = np.zeros(n)
    for mult, gain in partials:
        sig += gain * np.sin(2 * np.pi * freq * mult * t + mult)
    return amp * env * sig / 1.8


def _band_noise(n: int, low: float, high: float, rng) -> np.ndarray:
    """White noise shaped into a frequency band with an FFT mask."""
    spec = np.fft.rfft(rng.standard_normal(n))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    mask = ((freqs >= low) & (freqs <= high)).astype(float)
    # soften the edges to avoid metallic ringing
    width = max(1.0, (high - low) * 0.08)
    mask *= np.clip((freqs - (low - width)) / width, 0, 1)
    mask *= np.clip(((high + width) - freqs) / width, 0, 1)
    return np.fft.irfft(spec * mask, n)


def _clock_tick(rng, amp=0.055):
    t = np.arange(_n(0.06)) / SR
    click = 0.7 * rng.standard_normal(len(t)) + np.sin(2 * np.pi * 1750 * t)
    return amp * click * np.exp(-t * 95)


def _heartbeat(amp=0.42):
    t = np.arange(_n(0.22)) / SR
    return amp * np.sin(2 * np.pi * 47 * t) * np.exp(-t * 21)


def _reverb(signal: np.ndarray, delays=(0.11, 0.23, 0.37, 0.53), gains=(0.3, 0.19, 0.11, 0.06)):
    out = signal.copy()
    for delay, gain in zip(delays, gains):
        k = int(delay * SR)
        out[k:] += signal[:-k] * gain
    return out


def _loop(signal: np.ndarray, crossfade: float = 1.6) -> np.ndarray:
    """Crossfade the tail into the head so the WAV loops without a click."""
    xf = int(crossfade * SR)
    if len(signal) <= xf * 2:
        return signal
    head = signal[:xf].copy()
    tail = signal[-xf:].copy()
    fade = np.linspace(0.0, 1.0, xf)
    out = signal[:-xf].copy()
    out[:xf] = head * fade + tail * (1.0 - fade)
    return out


def _write(path: Path, signal: np.ndarray, level: float = 0.55) -> None:
    signal = np.asarray(signal, dtype=float)
    peak = float(np.max(np.abs(signal))) or 1.0
    signal = signal / peak * level
    pcm = (np.clip(signal, -1, 1) * np.iinfo(np.int16).max).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())


# ------------------------------------------------------------------- tracks
def midnight_manor() -> np.ndarray:
    n = _n(DURATION)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    mix = np.zeros(n)

    drone = (
        0.16 * np.sin(2 * np.pi * 55 * t)
        + 0.10 * np.sin(2 * np.pi * 82.5 * t + 1.3)
        + 0.06 * np.sin(2 * np.pi * 110 * t + 0.4)
    )
    mix += drone * (0.76 + 0.24 * np.sin(2 * np.pi * 0.045 * t))

    for start in (1.5, 9.5, 17.5, 25.5):
        _mix_into(mix, _pad([220.0, 261.63, 329.63], 8.0, amp=0.15, rng=rng), start)

    for start in np.arange(0.7, DURATION - 1.0, 2.4):
        _mix_into(mix, _heartbeat(), start)
        _mix_into(mix, _heartbeat(0.27), start + 0.31)

    for start in np.arange(0.9, DURATION - 0.2, 1.2):
        _mix_into(mix, _clock_tick(rng), start)

    mix += 0.018 * np.sin(2 * np.pi * 1046.5 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.09 * t))
    return mix


def rain_on_the_case_file() -> np.ndarray:
    n = _n(DURATION)
    t = np.arange(n) / SR
    rng = np.random.default_rng(23)
    mix = np.zeros(n)

    rain = _band_noise(n, 700, 7200, rng)
    rain *= 0.23 * (0.82 + 0.12 * np.sin(2 * np.pi * 0.13 * t) + 0.06 * np.sin(2 * np.pi * 0.43 * t))
    mix += rain

    for drop in range(190):
        start = rng.uniform(0, DURATION - 0.25)
        freq = rng.uniform(1100, 3400)
        length = rng.uniform(0.03, 0.11)
        tt = np.arange(_n(length)) / SR
        ping = np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 42) * rng.uniform(0.012, 0.042)
        _mix_into(mix, ping, start)

    for start in (4.0, 15.5, 27.0):
        length = 4.2
        rumble = _band_noise(_n(length), 28, 130, rng)
        tt = np.arange(len(rumble)) / SR
        env = np.exp(-tt * 1.15) * np.clip(tt / 0.5, 0, 1)
        _mix_into(mix, 0.26 * rumble * env, start)

    _mix_into(mix, _pad([110.0, 164.81, 220.0], DURATION, amp=0.09, rng=rng), 0)
    for start in np.arange(1.3, DURATION - 0.3, 1.6):
        _mix_into(mix, _clock_tick(rng, amp=0.035), start)
    return mix


def shadows_in_the_hall() -> np.ndarray:
    n = _n(DURATION)
    t = np.arange(n) / SR
    rng = np.random.default_rng(37)
    mix = np.zeros(n)

    mix += 0.05 * np.sin(2 * np.pi * 49 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
    _mix_into(mix, _pad([196.0, 207.65, 293.66], DURATION, amp=0.12, rng=rng, attack=3.0, release=4.0), 0)

    melody = [
        (1.0, 440.00), (4.6, 523.25), (8.1, 659.25), (11.6, 587.33),
        (15.1, 523.25), (18.6, 493.88), (22.1, 440.00), (25.6, 523.25),
        (28.4, 659.25), (30.2, 587.33),
    ]
    for start, freq in melody:
        _mix_into(mix, _reverb(_bell(freq, 3.4, amp=0.16, rng=rng), gains=(0.26, 0.15, 0.08)), start)

    mix += 0.012 * np.sin(2 * np.pi * 1318.5 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t))
    return mix


def the_interrogation() -> np.ndarray:
    n = _n(DURATION)
    t = np.arange(n) / SR
    rng = np.random.default_rng(53)
    mix = np.zeros(n)

    beat = 60.0 / 84.0  # 84 BPM
    chords = [
        [146.83, 174.61, 220.00],  # D minor
        [146.83, 174.61, 220.00],
        [116.54, 146.83, 174.61],  # B flat
        [110.00, 138.59, 164.81],  # A
    ]

    # pulsing bass, two bars of pulse then two bars of space
    for i in range(int(DURATION / beat)):
        start = i * beat
        if (i // 4) % 2 == 0:
            tt = np.arange(_n(beat * 0.55)) / SR
            bass = (
                np.sin(2 * np.pi * 55 * tt)
                + 0.35 * np.sin(2 * np.pi * 110 * tt)
                + 0.12 * rng.standard_normal(len(tt))
            )
            bass *= np.exp(-tt * 7) * 0.28
            _mix_into(mix, bass, start)

    # brushed hats on the off-beat
    for i in range(int(DURATION / (beat / 2))):
        start = i * beat / 2
        tt = np.arange(_n(0.05)) / SR
        hat = rng.standard_normal(len(tt)) * np.exp(-tt * 60) * 0.045
        _mix_into(mix, hat, start + 0.01)

    # chord stabs every two bars
    for bar in range(int(DURATION / (beat * 4))):
        chord = chords[bar % len(chords)]
        tt = np.arange(_n(1.9)) / SR
        stab = np.zeros(len(tt))
        for freq in chord:
            stab += np.sin(2 * np.pi * freq * tt) + 0.25 * np.sin(2 * np.pi * freq * 2 * tt)
        stab /= len(chord)
        stab *= np.exp(-tt * 2.4) * np.clip(tt / 0.03, 0, 1) * 0.22
        _mix_into(mix, stab, bar * beat * 4)

    # held dissonant note
    mix += 0.014 * np.sin(2 * np.pi * 466.16 * t) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t))
    return mix


def case_closed() -> np.ndarray:
    n = _n(DURATION)
    t = np.arange(n) / SR
    rng = np.random.default_rng(71)
    mix = np.zeros(n)

    chords = [
        [146.83, 174.61, 220.00],  # D minor
        [116.54, 146.83, 174.61],  # B flat
        [174.61, 220.00, 261.63],  # F major
        [130.81, 164.81, 196.00],  # C major
    ]
    for i, chord in enumerate(chords):
        _mix_into(mix, _pad(chord, 8.4, amp=0.2, rng=rng, attack=1.0, release=2.2), i * 8.0)

    melody = [
        (1.8, 587.33), (6.0, 698.46), (10.2, 880.00), (14.2, 783.99),
        (18.2, 698.46), (22.4, 659.25), (26.4, 587.33), (29.6, 880.00),
    ]
    for start, freq in melody:
        _mix_into(mix, _reverb(_bell(freq, 3.8, amp=0.2, rng=rng), gains=(0.3, 0.18, 0.1)), start)

    mix += 0.04 * np.sin(2 * np.pi * 73.42 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t))
    brush = _band_noise(n, 1800, 6500, rng)
    mix += 0.02 * brush * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t))
    return mix


def case_solved_sting() -> np.ndarray:
    """A short dramatic hit for the moment the accusation lands."""
    duration = 4.6
    n = _n(duration)
    mix = np.zeros(n)
    rng = np.random.default_rng(99)

    t = np.arange(_n(1.3)) / SR
    boom = np.sin(2 * np.pi * 45 * t) * np.exp(-t * 3.4) * 0.85
    _mix_into(mix, boom, 0)

    _mix_into(mix, _pad([146.83, 174.61, 220.00, 293.66], 4.2, amp=0.34,
                        rng=rng, attack=1.35, release=1.4), 0.1)
    _mix_into(mix, _pad([73.42, 110.00, 146.83], 2.9, amp=0.28,
                        rng=rng, attack=0.15, release=1.6), 1.7)
    _mix_into(mix, _reverb(_bell(587.33, 3.0, amp=0.34, rng=rng), gains=(0.3, 0.2, 0.1)), 1.45)
    _mix_into(mix, _reverb(_bell(880.00, 2.7, amp=0.2, rng=rng), gains=(0.28, 0.16)), 2.2)
    return mix


GENERATORS = {
    "midnight": midnight_manor,
    "rain": rain_on_the_case_file,
    "shadows": shadows_in_the_hall,
    "interrogation": the_interrogation,
    "closed": case_closed,
}


def ensure_tracks() -> Path:
    """Create any missing soundtrack files and return the audio directory."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for track in TRACKS:
        path = AUDIO_DIR / track["file"]
        if not path.exists() or path.stat().st_size < 200_000:
            _write(path, _loop(GENERATORS[track["id"]]()))

    sting = AUDIO_DIR / STING_FILE
    if not sting.exists() or sting.stat().st_size < 100_000:
        _write(sting, case_solved_sting(), level=0.7)
    return AUDIO_DIR


if __name__ == "__main__":
    ensure_tracks()
    for track in TRACKS:
        path = AUDIO_DIR / track["file"]
        with wave.open(str(path), "rb") as handle:
            seconds = handle.getnframes() / handle.getframerate()
        print(f"{path.name:32s} {seconds:5.1f}s  {path.stat().st_size / 1_048_576:4.2f} MB")
