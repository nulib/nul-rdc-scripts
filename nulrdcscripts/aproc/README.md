# aproc
A script for processing and performing QC on audio preservation files.

## Prerequisites
The following programs must be installed to use all of the script's functions:
- [ffmpeg](https://ffmpeg.org/) (must be compiled with libsoxr)
- ffprobe (included with ffmpeg)
- [SoX](https://sox.sourceforge.net/)
- [BWFMetaEdit](https://mediaarea.net/BWFMetaEdit)
- [MediaConch](https://mediaarea.net/MediaConch)
- [Poetry](https://python-poetry.org/)

## Usage
In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.

> **Note:** A valid inventory CSV must be present in the input folder or specified with `-l`.  
> **Note:** A QC log is always generated — MediaConch policies are always checked regardless of other flags.

### Basic usage
```
poetry run aproc -i INPUT_PATH
```

All processing steps run by default: transcoding, BWF metadata embedding, JSON sidecar generation, and spectrogram generation. Individual steps can be disabled with `--no-` flags.

### Disable specific steps
```
poetry run aproc -i INPUT_PATH --no-transcode
poetry run aproc -i INPUT_PATH --no-spectrogram
poetry run aproc -i INPUT_PATH --no-transcode --no-spectrogram
```

### Generate QC log only
```
poetry run aproc -i INPUT_PATH --no-transcode --no-write_metadata --no-write_json --no-spectrogram
```

### Expected input file structure
```
project folder (script input)
├── inventory.csv
├── item_1
│   └── p
│       └── item_1_v01_p.wav
└── item_2
    └── p
        ├── item_2_v01s01_p.wav
        └── item_2_v01s02_p.wav
```

---

## Commands

| Flag | Description |
|------|-------------|
| `-h`, `--help` | Show help message and exit |
| `-i`, `--input INPUT_PATH` | Full path to input folder |
| `-o`, `--output OUTPUT_PATH` | Full path to output CSV file for QC results. Defaults to a file in the input directory |
| `-a`, `--all` | Equivalent to using `-t -m -j -s` together |
| `-t`, `--transcode` / `--no-transcode` | Transcode access files (default: on) |
| `-m`, `--write_metadata` / `--no-write_metadata` | Write Broadcast WAVE metadata to preservation file (default: on) |
| `-j`, `--write_json` / `--no-write_json` | Write metadata to JSON sidecar file (default: on) |
| `-s`, `--spectrogram` / `--no-spectrogram` | Generate spectrograms (default: on) |
| `--skip_coding_history` | Skip coding history creation |
| `-l`, `--load_inventory INVENTORY_PATH` | Specify a CSV inventory file. If not provided, the script looks for CSV files in the input folder |
| `--sox SOX_PATH` | Custom path to SoX |
| `--bwfmetaedit METAEDIT_PATH` | Custom path to BWFMetaEdit |
| `--ffmpeg FFMPEG_PATH` | Custom path to ffmpeg |
| `--ffprobe FFPROBE_PATH` | Custom path to ffprobe |
| `--mediaconch MEDIACONCH_PATH` | Custom path to MediaConch |
| `--p_policy INPUT_POLICY` | MediaConch policy for preservation files |
| `--a_policy OUTPUT_POLICY` | MediaConch policy for access files |

---

## Inventory CSV

The inventory CSV drives both the BWF metadata embedding and the JSON sidecar output. The script looks for the following columns (some have legacy aliases that are also accepted):

| Column | Notes |
|--------|-------|
| `work_accession_number` | |
| `filename` | |
| `label` | |
| `description` | also accepts `inventory_title` |
| `record date/time` | |
| `housing/container markings` | also accepts `housing markings` or `container markings` |
| `condition notes` | |
| `barcode` | |
| `call number` | |
| `box/folder alma number` | |
| `format` | written to BWF ISRF field |
| `running time (mins)` | |
| `tape brand` | saved to JSON metadata |
| `speed IPS` | saved to JSON metadata |
| `tape thickness` | |
| `base (acetate/polyester)` | |
| `track configuration` | |
| `length/reel size` | |
| `sound` | |
| `tape type (cassette)` | saved to JSON metadata |
| `noise reduction` | saved to JSON metadata |
| `capture date` | normalized to YYYY-MM-DD |
| `digitizer` | also accepts `staff initials` |
| `digitizer notes` | also accepts `capture notes` |
| `capture device` | optional — see [Deck Configuration](#deck-configuration) |

---

## Deck Configuration

The script uses `data/deckconfig.json` as a lookup table for building the BWF Coding History field. Rather than entering equipment details row by row in the inventory, you enter the name of the capture setup in the `capture device` column and the script looks up the full equipment chain from the config.

### How it works

Each top-level key in `deckconfig.json` is a capture setup name that matches what you enter in the inventory's `capture device` column. Each setup contains one or more components, and each component becomes one line in the Coding History.

### Example deckconfig.json entry

Each entry is keyed by the playback deck name and rack number. The A/D converter and its parameters are defined in the same entry since each deck is permanently paired with a specific A/D per rack.

```json
"Yamaha C300 Rack 1": {
    "Playback Deck": {
        "deck_name": "Yamaha C300",
        "deck_nuTag": "E034942RT",
        "deck_algorithm": "ANALOG",
        "deck_mode": "stereo"
    },
    "A/D Converter": {
        "ad_name": "Metric Halo LIO8 MKIV",
        "ad_nuTag": "48276",
        "ad_algorithm": "PCM",
        "ad_samplerate": "96000",
        "ad_wordlength": "24",
        "ad_mode": "stereo"
    }
}
```

### Example inventory entry

| filename | ... | capture device |
|----------|-----|----------------|
| item_1_v01 | ... | Yamaha C300 Rack 1 |

### Generated Coding History

```
A=ANALOG,M=stereo,T=Yamaha C300; E034942RT
A=PCM,F=96000,W=24,M=stereo,T=Metric Halo LIO8 MKIV; 48276
A=PCM,F=96000,W=24,M=stereo,T=BWFMetaEdit 21.09
```

The final `A=PCM` line is always appended automatically at embed time, reflecting the actual technical properties of the file as reported by ffprobe (sample rate, bit depth, channel count) and the version of BWFMetaEdit used.

### Fallback behavior

If the `capture device` column is absent or empty for a row, the script falls back to building the Coding History from the `Encoding Chain` columns in the inventory (legacy behavior).

### Item-level tape details

Tape brand, speed, cassette type, and noise reduction are recorded in the JSON sidecar under `Inventory Metadata` rather than in the Coding History. This keeps the Coding History focused on the equipment chain and avoids mixing item-level descriptive data into a field intended to document signal processing.

---

## BWF and FADGI Compliance

Embedded metadata targets compliance with the [FADGI Guidelines for Embedding Metadata in Broadcast WAVE Files](https://www.digitizationguidelines.gov/guidelines/digitize-embedding.html), which are based on the EBU Broadcast WAVE Format specification (EBU Tech 3285) and EBU Technical Recommendation R98-1999 for the Coding History field.

### FADGI extension for sample rate

The base EBU R98 specification only lists sample rates up to 48000 Hz as valid values for the `F=` field in Coding History. FADGI explicitly extends this to include 96000, 176400, 192000, 384000, and 768000 Hz to reflect current digitization practice. The 96000 Hz sample rate used for preservation masters at Northwestern is therefore valid under FADGI even though it falls outside the original EBU spec.

### T= field

The `T=` free text field in each Coding History line has one constraint: it must not contain commas. Device names and NuTags in `deckconfig.json` should be checked to ensure they do not include commas.

### RF64

Standard BWF/WAV files have a 4GB size limit. RF64 is an extension of the BWF container that lifts this limit for very long recordings. At 96kHz/24bit stereo, the 4GB limit is reached at approximately 5.8 hours of audio.

RF64 files retain the full BWF `bext` chunk including all embedded metadata, so Coding History and all other fields are written and validated identically. BWFMetaEdit supports RF64 natively, meaning the script's embed commands work without modification regardless of whether the file is standard BWF or RF64.

Northwestern uses RF64 only when recordings exceed the 4GB threshold. For the vast majority of items standard BWF is used. The distinction is a container concern only — it has no effect on metadata compliance or the script's behavior.

> **Note:** Some older tools cannot read RF64 files. This is relevant for access copies and downstream use, not for the preservation master itself.

---

## Terminal help

Change directory:
```
cd FILEPATH          # absolute or relative path
cd ..                # go up one level
cd                   # return to home directory
```

List directory contents:
```
dir                  # Windows
ls                   # Linux / macOS
```

Clear terminal:
```
cls                  # Windows
clear                # Linux / macOS
```