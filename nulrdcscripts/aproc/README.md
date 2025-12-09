# aproc
A script for audio preservation file processing, quality control, and access copy generation.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed:
- **ffmpeg** (required - must have libsoxr support)
- **ffprobe** (required)
- **mediaconch** (required)
- **sox** (required)
- **bwfmetaedit** (required)
- **poetry** (for Python dependency management)

## Quick Start

The script **auto-detects** whether you're processing a single audio object or a batch, so you don't need to specify batch mode!

```bash
# Process everything with defaults
poetry run aproc -i INPUT_PATH

# That's it! The script will:
# ✓ Auto-detect single vs batch mode
# ✓ Create p/, a/, meta/ folders automatically
# ✓ Add _p suffix to preservation files if needed
# ✓ Find inventory.csv automatically
# ✓ Create access copies (44.1kHz/16-bit)
# ✓ Embed BWF metadata
# ✓ Generate JSON metadata files
# ✓ Generate spectrograms for QC
# ✓ Create QC log CSV
```

## What Runs By Default

| Step | Default | Flag to Change |
|------|---------|----------------|
| Create access copies | ✓ ON | `--skip-transcode` to disable |
| Embed BWF metadata | ✓ ON | `--skip-metadata` to disable |
| Create JSON metadata | ✓ ON | `--skip-json` to disable |
| Generate spectrograms | ✓ ON | `--skip-spectrogram` to disable |

**Everything runs by default** - only use `--skip-*` flags when you DON'T want something.

## Usage

In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.

**Note:** The script will automatically find `inventory.csv` (or any `.csv` file) in the input folder. You can also specify a custom inventory with `-l`.

### Flexible Input Structures

The script accepts **any** of these input structures and will auto-organize them:

#### Option 1: Files directly in folder
```
input_folder/
├── inventory.csv
└── recording.wav
```

#### Option 2: Object subfolders (batch mode - auto-detected)
```
input_folder/
├── inventory.csv
├── object_1/
│   └── recording.wav
└── object_2/
    └── recording.wav
```

#### Option 3: Already organized (preserved as-is)
```
input_folder/
├── inventory.csv
├── object_1/
│   └── p/
│       └── object_1_p.wav
└── object_2/
    └── p/
        └── object_2_p.wav
```

**All become this after processing:**
```
input_folder/
├── inventory.csv
├── object_1/
│   ├── p/
│   │   ├── object_1_p.wav            # Preservation master (with BWF metadata)
│   │   └── object_1_p.md5            # Checksum
│   ├── a/
│   │   ├── object_1_a.wav            # Access copy (44.1kHz/16-bit)
│   │   └── object_1_a.md5            # Checksum
│   └── meta/
│       ├── object_1_s.json           # Metadata
│       └── object_1_spectrogram_s.png # QC spectrogram
└── qc_log.csv                        # QC results
```

## Common Commands

### Basic Processing
```bash
# Process with all defaults (recommended)
poetry run aproc -i INPUT_PATH

# Use custom inventory location
poetry run aproc -i INPUT_PATH -l /path/to/inventory.csv

# Custom QC log output location
poetry run aproc -i INPUT_PATH -o /path/to/qc_log.csv
```

### Skip Specific Steps
```bash
# Skip creating access copies
poetry run aproc -i INPUT_PATH --skip-transcode

# Skip embedding BWF metadata
poetry run aproc -i INPUT_PATH --skip-metadata

# Skip generating JSON files
poetry run aproc -i INPUT_PATH --skip-json

# Skip generating spectrograms
poetry run aproc -i INPUT_PATH --skip-spectrogram

# Combine multiple skips
poetry run aproc -i INPUT_PATH --skip-spectrogram --skip-json
```

## All Command Options

### Core Options
`--input`, `-i INPUT_PATH`  
Full path to input folder containing .wav files. The script auto-detects whether to process as single object or batch.

`--output`, `-o OUTPUT_PATH`  
Full path to output CSV file for QC results. If not specified, defaults to creating a file in the input directory named `<basename>-qc_log.csv`.

`--inventory`, `-l INVENTORY_PATH`  
Path to CSV inventory file(s). If not specified, the script will auto-detect .csv files in the input folder. Can specify multiple files.

### Processing Control
All steps are **enabled by default**. Use these flags to **disable** specific steps:

`--skip-transcode`  
Skip creating access copies (44.1kHz/16-bit). Preservation files will still be processed.

`--skip-metadata`  
Skip embedding BWF (Broadcast WAVE Format) metadata into preservation files.

`--skip-json`  
Skip creating JSON metadata sidecar files.

`--skip-spectrogram`  
Skip generating spectrograms for QC (speeds up processing).

`--verbose`, `-v`  
Display detailed processing information (useful for debugging).

### Advanced Options
`--skip-coding-history`  
Skip coding history creation in BWF metadata. Use this if your inventory lacks encoding chain information.

`--p-policy POLICY_PATH`  
Custom MediaConch policy for preservation file validation.

`--a-policy POLICY_PATH`  
Custom MediaConch policy for access file validation.

### Custom Tool Paths
Only include if trying to use a version of the listed tool other than the system version or if the tool is not installed in the current path.

`--ffmpeg FFMPEG_PATH`  
Path to ffmpeg executable.

`--ffprobe FFPROBE_PATH`  
Path to ffprobe executable.

`--sox SOX_PATH`  
Path to sox executable.

`--bwfmetaedit METAEDIT_PATH`  
Path to bwfmetaedit executable.

`--mediaconch MEDIACONCH_PATH`  
Path to mediaconch executable.

## Inventory CSV Requirements

Your inventory CSV must include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `filename` | Base filename (without `_p` suffix) | `object1` |
| `work_accession_number` | Unique identifier | `2024-001` |
| `description` | Content description | `Interview recording` |
| `format` | Original source format | `cassette`, `reel-to-reel` |
| `capture date` | Digitization date | `2024-01-15` |
| `digitizer` | Person who digitized | `JD` |

### Optional Columns (for BWF Metadata)
- `encoding chain 1 hardware` - Playback device info
- `encoding chain 1 mode` - Audio mode (mono/stereo)
- `encoding chain 1 digital characteristics` - Sample rate; bit depth
- `tape brand`, `speed IPS`, `noise reduction` - Source details

**Important:** Use base filename WITHOUT the `_p` suffix in the CSV!
- ✓ Correct: `object1`
- ✗ Wrong: `object1_p`

### Example CSV
```csv
filename,work_accession_number,description,format,capture date,digitizer
object1,2024-001,Interview with Jane Doe,cassette,2024-01-15,JD
object2,2024-002,Concert recording,reel-to-reel,2024-01-16,JD
```

## Output Files

For each audio object, the script generates:

```
object_name/
├── p/
│   ├── object_name_p.wav              # Preservation master (with BWF metadata)
│   └── object_name_p.md5              # MD5 checksum
├── a/
│   ├── object_name_a.wav              # Access copy (44.1kHz/16-bit)
│   └── object_name_a.md5              # MD5 checksum
└── meta/
    ├── object_name_s.json             # Technical & descriptive metadata
    └── object_name_spectrogram_s.png  # QC spectrogram
```

Plus a QC log at the collection level:
```
collection_name-qc_log.csv             # Quality control results
```

## Quality Control

The QC log (`qc_log.csv`) contains results for:
- **Inventory check** - File found in CSV (PASS/FAIL)
- **MediaConch validation** - Technical specification compliance (PASS/FAIL)
  - Preservation Format Policy (96kHz/24-bit PCM WAV)
  - BWF Policy (Broadcast WAVE metadata)
- **Runtime** - File duration
- **Filenames** - Preservation and access copy names

Review the QC log after processing and address any FAIL entries.

## BWF Metadata

When metadata embedding is enabled (default), the script embeds:
- **ISRF** (Origination Source Form) - Source format from inventory
- **Coding History** - Complete encoding chain from digitization
- **MD5 Hash** - Embedded checksum for fixity verification
- **BextVersion** - Set to version 1

Coding history follows EBU recommendations:
```
A=PCM,F=96000,W=24,M=stereo,T=Playback Device; Device ID
```

## Technical Specifications

### Preservation Format (Input/Maintained)
- Container: WAV (RIFF)
- Codec: PCM (uncompressed)
- Sample Rate: 96 kHz
- Bit Depth: 24-bit
- Metadata: BWF (Broadcast WAVE Format)

### Access Format (Created)
- Container: WAV (RIFF)
- Codec: PCM (uncompressed)
- Sample Rate: 44.1 kHz
- Bit Depth: 16-bit
- Resampler: SoXR (high-quality)

## Troubleshooting

### "❌ NO FILES FOUND: No .wav files"
**Solution:** Ensure your input contains `.wav` files. The script only processes WAV files.

### "⚠️ WARNING: No inventory CSV found"
**Impact:** Script continues but metadata fields will be empty.  
**Solution:** Add an `inventory.csv` file to your input directory or specify with `-l` flag.

### "unable to locate file in csv data"
**Solution:** Check that filenames in your CSV match actual files (without `_p` suffix).
- File: `object1_p.wav`
- CSV should have: `object1` (not `object1_p`)

### "WARNING: ffmpeg is not configured with libsoxr"
**Solution:** Reinstall ffmpeg with libsoxr support:
```bash
# macOS
brew reinstall ffmpeg

# Check for libsoxr
ffmpeg -version | grep libsoxr
```

### "Error locating ffmpeg/sox/mediaconch/bwfmetaedit"
**Solution:** Install missing tools:
```bash
# macOS
brew install ffmpeg sox mediaconch bwfmetaedit

# Or specify custom paths
poetry run aproc -i /path --ffmpeg /custom/ffmpeg --sox /custom/sox
```

### Processing is slow
**Solutions:**
- Skip spectrograms: `--skip-spectrogram`
- Process smaller batches
- Move files to local disk if on network storage

## Tips & Best Practices

1. **Always include an inventory CSV** - Essential for proper BWF metadata
2. **Test with one file first** - Verify settings before batch processing
3. **Check the QC log** - Review for FAIL entries after processing
4. **Let defaults work** - Everything runs automatically unless you skip it
5. **Use verbose mode** - Add `--verbose` when troubleshooting
6. **Organize by object** - One folder per physical item/tape
7. **Keep original files** - Until you've verified all outputs

## Common Workflows

### Standard Processing (Recommended)
```bash
poetry run aproc -i /path/to/audio
```
Creates access copies, embeds metadata, generates JSON and spectrograms.

### Preservation Masters Only
```bash
poetry run aproc -i /path --skip-transcode
```
Embeds BWF metadata and creates spectrograms without access copies.

### Quick QC Check
```bash
poetry run aproc -i /path --skip-transcode --skip-spectrogram
```
Validates against MediaConch policies and creates QC log only.

### Metadata Only
```bash
poetry run aproc -i /path --skip-transcode --skip-spectrogram --skip-metadata
```
Only creates JSON metadata files and QC log.

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
which sox
which mediaconch
which bwfmetaedit

# Check versions
ffmpeg -version
sox --version
mediaconch -v
bwfmetaedit --Version
```

### Verify ffmpeg has libsoxr
```bash
ffmpeg -version | grep libsoxr
# Should show: --enable-libsoxr
```