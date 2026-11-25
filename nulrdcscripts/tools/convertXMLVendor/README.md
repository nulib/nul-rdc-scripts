# EmbedExtract

Converts vendor MediaAsset XML delivery files (MediaPreserve, Preserve South) into a flat table — `.xlsx` by default, or TSV — for Excel and OpenRefine. One row per barcode, with preservation and access master columns grouped per side.

## Requirements

- Python 3.7+
- `openpyxl` for `.xlsx` output (included in the poetry environment; run `poetry install`). `--tsv` output needs only the standard library.

## Usage

```bash
poetry run convertMP -i <folder> [-o <output.xlsx>] [--tsv]
```

### Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--input` | `-i` | Yes | Path to a folder containing vendor XML files. Searched recursively. |
| `--output` | `-o` | No | Output filename. Defaults to `<foldername>_xml_converted.xlsx` inside the input folder. A name ending in `.tsv` writes a TSV. |
| `--tsv` | | No | Write a tab-separated file instead of `.xlsx`. |

### Examples

```bash
# Basic batch run
python embedextract.py -i /path/to/Batch_01/

# Custom output filename
python embedextract.py -i ~/Desktop/Batch_01/ -o batch01_metadata.tsv
```

## Output

An `.xlsx` workbook (or TSV with `--tsv`) that opens in Excel and imports directly into OpenRefine. In the `.xlsx`, every cell is stored and formatted as Text, so barcodes don't turn into scientific notation and leading zeros (e.g. deck serial `0080266`) are kept, on any machine, with no Excel settings needed. Each row corresponds to one barcode. Vendors that deliver one XML per side (Preserve South: `_v01s01_s.xml`, `_v01s02_s.xml`) are merged into a single row; see **Merging per-side XMLs** below. Columns are ordered as:

1. **Base fields** — item-level metadata from the `<Original>` section (accession number, barcode, format, transfer comments, digitizer, deck/equipment info, etc.)
2. **Side columns** — two columns per side, in order `side 1 preservation`, `side 1 access`, `side 2 preservation`, `side 2 access`, etc. Vendor face designations are converted to side numbers (A → 1, B → 2, etc.). Each cell consolidates that file's technical metadata as `label: value` pairs separated by `; `, skipping empty values, e.g.:

   `filename: ..._p.wav; running time: 00:24:33; sample rate: 96000; bit per sample: 24; bit rate: 4608000; sound field from jhove: 2; file size bytes: 848393168; checksum type: SHA-256; checksum: e005...; checksum date created: 2026-11-20`

   Fields and their order are set by `FILE_FIELDS` in the script.

Sides are detected dynamically from each XML file, so batches with non-standard or additional face labels (e.g. C, D → sides 3, 4) are handled without any code changes.

### Field transformations

- **Running time** — the carrier `running time mins` column is converted from `HH:MM:SS` to integer minutes, rounded up; file running times stay `HH:MM:SS`
- **Capture date** — taken from the first side's preservation master `DateCreated`, falling back to `ChecksumDateCreated` (Preserve South)
- **Dates** — datetime strings (`2025-11-04T09:47:02`) are truncated to date only (`2025-11-04`)
- **Transfer comments** — `Baked` and `Cleaned` values are appended to the `TransferComments` field
- **Digitizer** — `Originator` and `TransferOperator` are merged into a single field, semicolon-separated
- **Placeholders** — vendor placeholder values (`N/A`, `NA`, `None`, `null`) are output as empty cells
- **Checksums** — read from `<Checksum>` (MediaPreserve) or `<ChecksumValue>` (Preserve South)
- **Photographs** — repeated `<Photograph>`/`<Checksum>`/`<FileSizeInKB>` groups (Preserve South) are written to `photographs`, `photograph checksums`, and `photograph file sizes kb`, semicolon-separated and in matching order

### Merging per-side XMLs

XMLs sharing a barcode are combined into one row:

- **Side columns** — taken from whichever XML contains that side
- **`running time mins`** — carrier running times summed across the XMLs, then rounded up to minutes
- **Photographs** — unioned and deduplicated by filename; `picture count` is the number of unique photos
- **`capture date`** — earliest date
- **`source file`** — all contributing XML filenames, semicolon-separated
- **Everything else** — a single value if every XML agrees; otherwise labeled per side, e.g. `side 1: Mono | side 2: Stereo`. Disagreements are also flagged in `discrepancies` (`sound differs between side XMLs`), except `transfer comments`, which are expected to differ per side.

### Discrepancies

The `discrepancies` column flags where the vendor's carrier notes disagree with the delivered files, or the files disagree with each other. Empty means no issues found. Checks:

- Carrier `RunningTime` vs. the sum of preservation master running times (exact, to the second)
- Preservation vs. access running time per side
- A side with a preservation master but no access master, or vice versa
- Carrier `SoundField` (Mono/Stereo) vs. channel count from `SoundFieldFromJhove` (a mono carrier captured to 2 channels is flagged)
- `PictureCount` vs. number of `<Photograph>` entries listed

- **Encoding chain omitted** — host computer, OS, A/D, DIO, encode software, and video correction device fields are not exported. Re-add them to `FILE_FIELDS` (and `BASE_FIELDNAMES` for video correction) if needed. File size KB/MB/GB are also omitted in favor of bytes.

### Vendor notes

- **Preserve South** does not supply `DateCreated`; `checksum date created` is the closest equivalent. Preserve South–only columns (tape width, reel size, tape type, pack orientation, cassette type, studio transfer method) are appended after the original base columns, so existing column positions are unchanged.

## Notes

- XML files are collected case-insensitively (`.xml` and `.XML`) and deduplicated, so the tool is safe to run on case-insensitive filesystems (macOS).
- Face designations are normalized to uppercase internally, so inconsistent casing from MediaPreserve (`a` vs `A`) does not produce duplicate columns.
- If a side has a preservation master but no access master (or vice versa), the missing column is left empty.
- Rows with no `<Original>` section will produce a warning and be skipped.

---

## OpenRefine workflow: filling metadata from the output

This workflow joins the output from EmbedExtract into your existing tracking spreadsheet using barcode as the key column.

### Prerequisites

- OpenRefine 3.7+
- Your tracking spreadsheet (CSV or TSV) loaded as **Project A**
- The EmbedExtract output (`.xlsx` or TSV) loaded as **Project B**

---

### Step 1 — Load both files into OpenRefine

1. Open OpenRefine and click **Create Project**
2. Import your tracking spreadsheet (e.g. `p1201_SchoolofMusicDAT_Audio.csv`) → name it something like `DAT_tracking`
3. Create a second project from your EmbedExtract output → name it something like `MediaPreserve_extracted`

Make sure both projects are open in separate browser tabs before proceeding.

---

### Step 2 — Verify barcode alignment

In **DAT_tracking**, check that barcodes are clean:

1. Click the dropdown arrow on the `barcode` column → **Facet > Text facet**
2. Scan for blanks, leading/trailing spaces, or inconsistent formatting
3. If needed: `barcode` column → **Edit cells > Common transforms > Trim whitespace**

Repeat in **MediaPreserve_extracted** on its `barcode` column.

---

### Step 3 — Add extracted columns via cross()

For each field you want to pull from the output, add a new column in **DAT_tracking** using a GREL `cross()` expression.

1. In **DAT_tracking**, click the `barcode` column dropdown → **Edit column > Add column based on this column**
2. Name the new column to match your target field (e.g. `running time (mins)`)
3. Enter the GREL expression:

```
cell.cross("MediaPreserve_extracted", "barcode")[0].cells["running time mins"].value
```

Repeat for each field, changing the source column name in quotes each time. Key mappings between the output and your tracking sheet:

| Tracking sheet column | EmbedExtract output column |
|---|---|
| `running time (mins)` | `running time mins` |
| `tape brand` | `stock brand` |
| `speed IPS` | `speed IPS` |
| `track configuration` | `track configuration` |
| `sound` | `sound` |
| `noise reduction` | `noise reduction` |
| `capture date` | `capture date` |
| `digitizer` | `digitizer` |
| `digitizer notes` | `transfer comments` |

> **Note:** file technical metadata is consolidated into `side N preservation` / `side N access` columns. If a tape has only one side, all data will be under side 1.

---

### Step 4 — Fill only blank cells (non-destructive)

If your tracking sheet already has some cells filled in that you don't want to overwrite, use a conditional expression:

```
if(isBlank(cells["running time (mins)"].value),
  cell.cross("MediaPreserve_extracted", "barcode")[0].cells["running time mins"].value,
  cells["running time (mins)"].value)
```

This leaves existing values untouched and only fills blanks.

---

### Step 5 — Handle unmatched barcodes

After running `cross()`, some cells may return blank because:

- The barcode exists in the tracking sheet but has no corresponding XML (not yet digitized)
- The barcode was not delivered in this batch

To identify unmatched rows:

1. On any newly filled column → **Facet > Customized facets > Facet by blank**
2. Select `true` to isolate rows where the join returned nothing
3. Review — these are items either not yet digitized or missing from the MediaPreserve delivery

---

### Step 6 — Export

1. Click **Export > Comma-separated value** (or Tab-separated, depending on your target)
2. Re-import into your original spreadsheet application as needed

---

### Tips

- **`cross()` is case-sensitive** — if barcodes differ in formatting between the two projects (e.g. integer vs string), apply `toString()`: `cell.cross("MediaPreserve_extracted", "barcode")[0]` may fail silently. Add `toString(value)` on both sides if joins return blank unexpectedly.
- **Column names with spaces** must be quoted exactly as they appear in the source project — OpenRefine is case- and space-sensitive here.
- **Undo is unlimited** in OpenRefine during a session — if a `cross()` expression produces unexpected results, use the Undo/Redo panel on the left to roll back.