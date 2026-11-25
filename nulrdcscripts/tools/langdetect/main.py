#!/usr/bin/env python3
"""
langdetect — detect spoken language at several points in audio/video files.

Samples N evenly spaced 30s windows (skipping the first/last 5% to avoid
leader, tone, and credits), runs Whisper language ID on each, and reports
per-point results plus a majority call. No transcription is done.

Requires: ffmpeg/ffprobe on PATH (whisper is installed via poetry)

Usage:
  poetry run langdetect -i file.mkv
  poetry run langdetect *.wav -n 6 --model medium --csv results.csv
"""
import argparse
import csv
import subprocess
import sys
from collections import Counter

import numpy as np
import whisper
from whisper.tokenizer import LANGUAGES

SR = 16000
CLIP = 30          # Whisper's analysis window (seconds)
SILENCE_DB = -50   # clips quieter than this (RMS dBFS) are skipped


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def extract(path, start):
    """Decode a 30s mono 16 kHz clip straight to a float array (no temp files)."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-nostdin", "-ss", f"{start:.3f}", "-t", str(CLIP),
         "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def sample_points(dur, n):
    if dur <= CLIP or n == 1:
        return [0.0]
    lo = dur * 0.05
    hi = max(dur * 0.95 - CLIP, lo)
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def detect(model, audio):
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    return lang, float(probs[lang])


def tc(s):
    s = int(s)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def process(path, model, n, min_conf):
    rows = []
    dur = duration(path)
    print(f"\n{path}  ({tc(dur)})")
    print(f"  {'#':>2}  {'time':8}  {'lang':4} {'name':14} {'conf':>5}")

    for i, start in enumerate(sample_points(dur, n), 1):
        audio = extract(path, start)
        rms = np.sqrt(np.mean(audio ** 2)) if audio.size else 0.0
        db = 20 * np.log10(rms) if rms > 0 else -120.0

        if db < SILENCE_DB:
            lang, name, conf, note = "", "", None, "silent"
        else:
            lang, conf = detect(model, audio)
            name = LANGUAGES.get(lang, lang).title()
            note = "low-conf" if conf < min_conf else ""

        conf_s = f"{conf:.3f}" if conf is not None else "  -  "
        print(f"  {i:>2}  {tc(start)}  {lang:4} {name:14} {conf_s}  {note}")
        rows.append({"file": path, "point": i, "time": tc(start), "lang": lang,
                     "language": name, "confidence": "" if conf is None else round(conf, 3),
                     "note": note})

    confident = [r["lang"] for r in rows if r["lang"] and r["note"] == ""]
    if confident:
        votes = Counter(confident)
        top, count = votes.most_common(1)[0]
        mixed = "  ** MIXED **" if len(votes) > 1 else ""
        print(f"  Majority: {top} ({LANGUAGES.get(top, top).title()}) {count}/{len(rows)}{mixed}")
    else:
        print("  Majority: none (no confident detections)")
    return rows


def main():
    ap = argparse.ArgumentParser(description="Whisper language ID at multiple points per file.")
    ap.add_argument("files", nargs="*", help="audio or video files")
    ap.add_argument("-i", "--input", nargs="+", default=[], help="audio or video files (same as positional)")
    ap.add_argument("-n", "--points", type=int, default=5, help="sample points per file (default 5)")
    ap.add_argument("--model", default="small", help="whisper model (tiny/base/small/medium/large-v3)")
    ap.add_argument("--min-conf", type=float, default=0.7, help="flag detections below this (default 0.7)")
    ap.add_argument("--csv", help="also write results to this CSV")
    args = ap.parse_args()
    files = args.files + args.input
    if not files:
        ap.error("no input files given")

    model = whisper.load_model(args.model)
    all_rows = []
    for f in files:
        try:
            all_rows += process(f, model, args.points, args.min_conf)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or str(e))
            print(f"\n{f}: ffmpeg/ffprobe failed (no audio stream?)\n  {err.strip().splitlines()[0]}",
                  file=sys.stderr)

    if args.csv and all_rows:
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=all_rows[0].keys())
            w.writeheader()
            w.writerows(all_rows)
        print(f"\nCSV written: {args.csv}")


if __name__ == "__main__":
    main()
