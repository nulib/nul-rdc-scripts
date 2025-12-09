# vproc
A script for video preservation file processing, quality control, and access copy generation.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed:
- **ffmpeg** (required)
- **ffprobe** (required)
- **mediaconch** (required)
- **qcli** (optional - only needed for QCTools reports with `--run-qcli`)
- **poetry** (for Python dependency management)

## Quick Start

The script **auto-detects** whether you're processing a single video or a batch, so you don't need to specify `-b` anymore!

```bash
# Process everything with defaults
poetry run vproc -i INPUT_PATH

# That's it! The script will:
# ✓ Auto-detect single vs batch mode
# ✓ Create p/, a/, meta/ folders automatically
# ✓ Add _p suffix to preservation files if needed
# ✓ Find inventory.csv automatically
# ✓ Create H.264/AAC access copies
# ✓ Generate JSON metadata files
# ✓ Generate spectrograms for audio QC
# ✗ QCTools reports are OFF by default (use --run-qcli to enable)
```

## What Runs By Default

| Step | Default | Flag to Change |
|------|---------|----------------|
| Create access copies | ✓ ON | `--skip-ac` to disable |
| Generate spectrograms | ✓ ON | `--skip-spectrogram` to disable |
| Create JSON metadata | ✓ ON | *(always runs)* |
| Generate QCTools reports | ✗ OFF | `--run-qcli` to enable |

## Usage

In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.

**Note:** The script will automatically find `transcode_inventory.csv` (or any `.csv` file) in the input folder. You can also specify a custom inventory with `-l`.

### Flexible Input Structures

The script accepts **any** of these input structures and will auto-organize them:

#### Option 1: Files directly in folder
```
input_folder/
├── transcode_inventory.csv
└── item.mkv
```

#### Option 2: Object subfolders (batch mode - auto-detected)
```
input_folder/
├── transcode_inventory.csv
├── item_1/
│   └── capture.mkv
└── item_2/
    └── capture.mkv
```

#### Option 3: Already organized (preserved as-is)
```
input_folder/
├── transcode_inventory.csv
├── item_1/
│   └── p/
│       └── item_1_p.mkv
└── item_2/
    └── p/
        └── item_2_p.mkv
```

**All become this after processing:**
```
input_folder/
├── transcode_inventory.csv
├── item_1/
│   ├── p/
│   │   └── item_1_p.mkv              # Preservation master
│   ├── a/
│   │   └── item_1_a.mp4              # Access copy
│   ├── meta/
│   │   ├── item_1_s.json             # Metadata
│   │   └── item_1_spectrogram00_s.png # QC spectrogram
│   └── qc_log.csv                    # QC results
└── item_2/
    └── (same structure)
```

## Common Commands

### Basic Processing
```bash
# Process with all defaults (recommended)
poetry run vproc -i INPUT_PATH

# Use custom inventory location
poetry run vproc -i INPUT_PATH -l /path/to/inventory.csv

# Custom output directory
poetry run vproc -i INPUT_PATH -o OUTPUT_PATH
```

### Enable/Disable Steps
```bash
# Enable QCTools reports (disabled by default)
poetry run vproc -i INPUT_PATH --run-qcli

# Skip creating access copies
poetry run vproc -i INPUT_PATH --skip-ac

# Skip generating spectrograms
poetry run vproc -i INPUT_PATH --skip-spectrogram

# Combine flags
poetry run vproc -i INPUT_PATH --skip-ac --skip-spectrogram
```

### Audio Mixdown Options
```bash
# Copy all audio streams as-is (default)
poetry run vproc -i INPUT_PATH --mixdown copy

# 4 mono → 1 stereo (tracks 1&2) + 2 mono (tracks 3&4)
poetry run vproc -i INPUT_PATH --mixdown 4to3

# 4 mono → 2 stereo (tracks 1&2, 3&4)
poetry run vproc -i INPUT_PATH --mixdown 4to2

# 2 mono → 1 stereo
poetry run vproc -i INPUT_PATH --mixdown 2to1
```

## All Command Options

### Core Options
`--input`, `-i INPUT_PATH`  
Full path to input folder containing .mkv files. The script auto-detects whether to process as single object or batch.

`--output`, `-o OUTPUT_PATH`  
Full path to output folder. If left blank, defaults to the input folder.

`--inventory`, `-l INVENTORY_PATH`  
Path to CSV inventory file. If not specified, the script will auto-detect .csv files in the input folder.

### Processing Control
`--skip-ac`  
Skip access copy transcoding. Preservation files will still be validated and organized.

`--skip-spectrogram`  
Skip audio spectrogram generation (speeds up processing).

`--run-qcli`  
Enable QCTools report generation. **Requires qcli to be installed.** Disabled by default because it significantly increases processing time.

`--mixdown MIXDOWN`  
Sets how audio streams will be mapped when transcoding the access copy.
- `copy` (default) - Copy all streams as-is
- `4to3` - Mix streams 1&2 to stereo, keep streams 3&4 as mono
- `4to2` - Mix streams 1&2 and 3&4 into two stereo streams  
- `2to1` - Mix streams 1&2 into one stereo stream

`--verbose`, `-v`  
Display detailed ffmpeg output when transcoding (useful for debugging).

### Advanced Options
`--keep-filename`  
Preserve original filename (don't add `_p` suffix to preservation files).

`--embed-framemd5`  
Remux preservation file to embed framemd5 checksums.

`--slices SLICE_COUNT`  
Set FFV1 slice count for encoding. Options: 4, 6, 9, 12, 16 (default), 24, 30.

`--input-policy POLICY_PATH`  
Custom MediaConch policy for input file validation.

`--output-policy POLICY_PATH`  
Custom MediaConch policy for output file validation.

### Custom Tool Paths
Only include if trying to use a version of the listed tool other than the system version or if the tool is not installed in the current path.

`--ffmpeg FFMPEG_PATH`  
Path to ffmpeg executable.

`--ffprobe FFPROBE_PATH`  
Path to ffprobe executable.

`--qcli QCLI_PATH`  
Path to qcli executable (only needed if using `--run-qcli`).

`--mediaconch MEDIACONCH_PATH`  
Path to mediaconch executable.

## Inventory CSV Requirements

Your inventory CSV must include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `filename` | Base filename (without `_p` suffix) | `item_1` |
| `work_accession_number` | Unique identifier | `2024-V-001` |
| `description` | Content description | `Home movie` |
| `format` | Original video format | `VHS`, `Betacam SP` |
| `capture date` | Digitization date | `2024-01-15` |
| `digitizer` | Person who digitized | `JD` |
| `vtr` | VTR/deck configuration key | `vhs_deck_1` |

**Important:** Use base filename WITHOUT the `_p` suffix in the CSV!
- ✓ Correct: `item_1`
- ✗ Wrong: `item_1_p`

## Output Files

For each video object, the script generates:

```
object_name/
├── p/
│   └── object_name_p.mkv              # Preservation master (FFV1/MKV)
├── a/
│   ├── object_name_a.mp4              # Access copy (H.264/AAC)
│   └── object_name_a.mp4.log          # Transcode log
├── meta/
│   ├── object_name_s.json             # Technical metadata
│   ├── object_name_spectrogram00_s.png # Audio QC (track 1)
│   └── object_name_spectrogram01_s.png # Audio QC (track 2)
└── qc_log.csv                         # Quality control results
```

Optional (with `--run-qcli`):
```
object_name_p.mkv.qctools.xml.gz       # QCTools report
```

## Quality Control

The QC log (`qc_log.csv`) contains results for:
- **Inventory check** - File found in CSV (PASS/FAIL)
- **MediaConch validation** - Technical specification compliance (PASS/FAIL)
- **Runtime** - File duration
- **Filenames** - Preservation and access copy names

Review the QC log after processing and address any FAIL entries.

## Audio Mixdown Examples

### Default (copy)
```
Input:  4 mono tracks
Output: 4 mono tracks (unchanged)
```

### 4to3 Mode
```
Input:  Track 1 (mono), Track 2 (mono), Track 3 (mono), Track 4 (mono)
Output: Track 1 (stereo from 1+2), Track 2 (mono from 3), Track 3 (mono from 4)
```

### 4to2 Mode
```
Input:  Track 1 (mono), Track 2 (mono), Track 3 (mono), Track 4 (mono)
Output: Track 1 (stereo from 1+2), Track 2 (stereo from 3+4)
```

### 2to1 Mode
```
Input:  Track 1 (mono), Track 2 (mono)
Output: Track 1 (stereo from 1+2)
```

## Technical Specifications

### Preservation Format (Input)
- Container: Matroska (MKV)
- Video: FFV1 (lossless)
- Audio: PCM (uncompressed)

### Access Format (Output)
- Container: MP4
- Video: H.264 (libx264, 8000 kbps, 2-pass)
- Audio: AAC (256 kbps)

## Troubleshooting

### "❌ NO FILES FOUND: No .mkv files"
**Solution:** Ensure your input contains `.mkv` files. The script only processes MKV containers.

### "unable to locate file in csv data"
**Solution:** Check that filenames in your CSV match actual files (without `_p` suffix).
- File: `item_1_p.mkv`
- CSV should have: `item_1` (not `item_1_p`)

### "Error locating ffmpeg/mediaconch"
**Solution:** Install missing tools or specify custom paths with `--ffmpeg` or `--mediaconch` flags.

### "Error locating qcli"
**Solution:** Either install qcli or don't use the `--run-qcli` flag. QCTools reports are optional.

### Access copy creation is slow
**This is normal** - 2-pass H.264 encoding is CPU-intensive. You can:
- Skip access copies during initial QC: `--skip-ac`
- Skip spectrograms: `--skip-spectrogram`
- Process fewer files at once

## Tips & Best Practices

1. **Start simple** - Just run with `-i /path` and let defaults work
2. **Test one file first** - Verify settings before batch processing
3. **Skip QCTools initially** - Only use `--run-qcli` when you need frame-level analysis
4. **Check QC logs** - Review for FAIL entries after processing
5. **Use appropriate mixdown** - Choose audio mapping based on your content
6. **Keep inventory updated** - Accurate CSV ensures proper metadata

## Common Workflows

### Standard Processing (Recommended)
```bash
poetry run vproc -i /path/to/video
```
Creates access copies, JSON metadata, and spectrograms. No QCTools reports.

### With QCTools Analysis (Comprehensive but Slow)
```bash
poetry run vproc -i /path/to/video --run-qcli
```
Adds frame-level QC analysis. Significantly increases processing time.

### Quick QC Check (Fast)
```bash
poetry run vproc -i /path/to/video --skip-ac --skip-spectrogram
```
Only validates preservation files and creates metadata.

### Custom Audio Configuration
```bash
poetry run vproc -i /path/to/video --mixdown 4to2
```
Creates 2 stereo tracks from 4 mono tracks in access copy.

## Terminal Help

### Change directory
`cd FILEPATH`
- Relative to current directory: `cd folder`
- Absolute path: `cd C:\folder\subfolder`
- Go back one folder: `cd ..`
- Return to your user folder: `cd`

### See contents of current directory
- `dir` (Windows)
- `ls` (Linux/macOS)

### Clear terminal
- `cls` (Windows)
- `clear` (Linux/macOS)

### Check if tools are installed
```bash
# Check each tool
which ffmpeg
which ffprobe
which mediaconch
which qcli

# Or check versions
ffmpeg -version
mediaconch -v
qcli -version
```