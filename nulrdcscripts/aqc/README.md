# audio_analysis.py

Audio quality control tool for loudness measurement, silence detection, and normalization recommendations. Generates detailed text reports against broadcast, streaming, or film standards.

---

## Requirements

- [Poetry](https://python-poetry.org/docs/#installation)
- Python 3.7+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your PATH

The script uses only the Python standard library — Poetry manages the environment and entry point, but installs no third-party packages.

**Install ffmpeg:**

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

---

## Setup

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install the project (creates a virtual environment automatically)
poetry install
```

After that you can run the tool two ways:

```bash
# Via the poetry-managed entry point (recommended)
poetry run aqc <file_or_folder> [options]

# Or drop into the virtual environment shell first
poetry shell
aqc <file_or_folder> [options]
```

---

## Usage

```bash
poetry run aqc <file_or_folder> [options]
```

The only required argument is one or more input files or a folder. Everything else has sensible defaults.

---

## Examples

**Single file — report saved beside the source:**
```bash
poetry run aqc interview.wav
# → interview_report.txt
```

**Entire folder — one report per file:**
```bash
poetry run aqc /recordings/session_01/
# → /recordings/session_01/track01_report.txt
# → /recordings/session_01/track02_report.txt
# → ...
```

**Multiple files with a glob:**
```bash
poetry run aqc *.flac
```

**Choose a loudness standard:**
```bash
poetry run aqc podcast.mp3 --standard streaming
```

**Save reports to a specific folder:**
```bash
poetry run aqc /recordings/ --output /reports/
```

**Override loudness target:**
```bash
poetry run aqc mix.wav --target-lufs -16 --max-true-peak -2
```

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--standard` | `broadcast` | Loudness standard: `broadcast`, `streaming`, or `film` |
| `--target-lufs` | *(from standard)* | Override integrated loudness target (LUFS) |
| `--max-true-peak` | *(from standard)* | Override true peak ceiling (dBTP) |
| `--output` / `-o` | beside source file | Report path (single file) or output directory (multiple files) |

---

## Standards

| Standard | Target | True Peak | Spec |
|----------|--------|-----------|------|
| `broadcast` | −23 LUFS | −1 dBTP | EBU R128 / ATSC A/85 |
| `streaming` | −14 LUFS | −1 dBTP | Spotify / Apple Music / YouTube |
| `film` | −24 LUFS | −2 dBTP | SMPTE Digital Cinema |

All standards use a ±1 LUFS tolerance window.

---

## What the Report Covers

- **Integrated loudness** — measured LUFS vs. target, deviation, and tolerance
- **True peak** — measured dBTP vs. standard maximum
- **Compliance checks** — pass/fail for LUFS, true peak, and silence
- **Silence detection** — timestamps of any dropout-length silent periods (≥0.5 s below −60 dB)
- **Quiet passages** — timestamps of naturally quiet sections (≥2 s below standard quiet threshold)
- **Recommendations** — severity-tagged: `CRITICAL`, `WARNING`, `INFO`, or `PASS`
- **Normalization command** — ready-to-run ffmpeg command for creating a normalized access copy (only generated when needed)

---

## Supported Formats

**Audio:** mp3, wav, flac, aac, ogg, m4a, aiff, aif, opus, wma, alac, ape, wv, mka

**Video (audio track extracted):** mp4, mkv, mov, avi, mxf, ts, m2ts, mts, wmv, webm, flv, ogv, 3gp

---

## Important Notes

**Reports are for the source file as-is.** The normalization command at the bottom of each report is for creating access or distribution copies only. Never apply normalization directly to a preservation master.

**Silence vs. quiet passages** are reported separately. Silence (below −60 dB) may indicate dropouts; quiet passages (below −40/−35/−50 dB depending on standard) are natural dynamic range and expected in most recordings.

**Batch summary** is printed to the terminal when processing more than one file, showing totals for pass / needs attention / failed.

---

## Report Example

```
======================================================================
AUDIO QUALITY CONTROL REPORT
======================================================================
File:     session_01_track02.wav
Standard: EBU R128 / ATSC A/85
Status:   NORMALIZATION RECOMMENDED ⚙
Date:     2026-05-11 14:32:07

======================================================================
LOUDNESS METRICS
======================================================================
Integrated Loudness:     -19.43 LUFS
Target Loudness:         -23.00 LUFS
Tolerance:                 1.00 LUFS
Deviation:                +3.57 dB

True Peak:                -0.83 dBTP
Maximum Allowed:          -1.00 dBTP

======================================================================
COMPLIANCE CHECKS
======================================================================
LUFS Compliance:       ✗ FAIL
True Peak Compliance:  ✗ FAIL
Silence Check:         ✓ PASS
Quiet Sections:        ✓ PASS

...
```

---

## License

MIT — use freely, attribution appreciated.
