Version Date: 11/25/2026

Document Owner: Sophia Francis

Software Used: ffmpeg, ffprobe, OpenAI Whisper

# Description
Detects the spoken language at several points in an audio or video file. No transcription is done.

The script samples evenly spaced 30-second windows (default 5), skipping the first and last 5% of the file to avoid leader, tone, and credits. It runs Whisper language ID on each window and reports the language and confidence for each point, plus a majority call for the file.

- **silent**: window is quieter than -50 dBFS and is skipped
- **low-conf**: confidence is below the threshold (default 0.7); not counted toward the majority
- **\*\* MIXED \*\***: confident detections disagree; check for multiple languages or misdetection

# Installation Instructions
This script runs through poetry and can be installed and updated from it.

```
poetry install
```
- Requires Python 3.10–3.14 and ffmpeg/ffprobe on PATH
- The first run downloads the Whisper model (`small` is ~460 MB), which is cached afterwards

## Usage

### Detect language in a file:
```
poetry run langdetect -i /path/to/input.wav
```

### Multiple files:
```
poetry run langdetect -i /path/to/file1.mkv /path/to/file2.wav
```

### Change the number of sample points (default 5):
```
poetry run langdetect -i /path/to/input -n 6
```

### Save results to a CSV:
```
poetry run langdetect -i /path/to/input --csv /path/to/results.csv
```

### Options
| Flag | Default | Description |
|---|---|---|
| `-i`, `--input` | | Audio or video file(s) |
| `-n`, `--points` | 5 | Sample points per file |
| `--model` | small | Whisper model: tiny, base, small, medium, large-v3 |
| `--min-conf` | 0.7 | Flag detections below this confidence |
| `--csv` | | Also write results to this CSV |

## Example Output
```
p1197_carl_35552001596203_v01s01_a.wav  (00:46:12)
   #  time      lang name            conf
   1  00:02:18  en   English        0.981
   2  00:12:51  en   English        0.964
   3  00:23:24  en   English        0.912
   4  00:33:57                        -    silent
   5  00:44:30  en   English        0.548  low-conf
  Majority: en (English) 3/5
```

## Notes
- Music-only sections can produce a confident but wrong language; review low-conf and MIXED results.
- Use `--model medium` for difficult audio (noisy, accented, or less common languages). It is slower.
