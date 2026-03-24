# EmbedExtract

Converts MediaPreserve XML delivery files into a flat TSV for OpenRefine processing. One row per barcode, with preservation and access master columns grouped side-by-side per face.

## Requirements

- Python 3.7+
- No external dependencies (standard library only)

## Usage

```bash
poetry run convertMP -i <folder> [-o <output.tsv>]
```

### Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--input` | `-i` | Yes | Path to a folder containing MediaPreserve XML files. Searched recursively. |
| `--output` | `-o` | No | Output TSV filename. Defaults to `<foldername>_xml_converted.tsv` inside the input folder. |

### Examples

```bash
# Basic batch run
python embedextract.py -i /path/to/Batch_01/

# Custom output filename
python embedextract.py -i ~/Desktop/Batch_01/ -o batch01_metadata.tsv
```

## Output

A tab-separated values (TSV) file suitable for direct import into OpenRefine. Each row corresponds to one XML file (one barcode). Columns are ordered as:

1. **Base fields** — item-level metadata from the `<Original>` section (accession number, barcode, format, transfer comments, digitizer, deck/equipment info, etc.)
2. **Face columns** — one group per face designation (A, B, C, etc.), each containing:
   - `face X pres <field>` — PreservationMaster technical metadata
   - `face X access <field>` — AccessMaster technical metadata

Face designations are detected dynamically from each XML file, so batches with non-standard or additional face labels (e.g. C, D) are handled without any code changes.

### Field transformations

- **Running time** — converted from `HH:MM:SS` to integer minutes, rounded up
- **Dates** — datetime strings (`2025-11-04T09:47:02`) are truncated to date only (`2025-11-04`)
- **Transfer comments** — `Baked` and `Cleaned` values are appended to the `TransferComments` field
- **Digitizer** — `Originator` and `TransferOperator` are merged into a single field, semicolon-separated

## Notes

- XML files are collected case-insensitively (`.xml` and `.XML`) and deduplicated, so the tool is safe to run on case-insensitive filesystems (macOS).
- Face designations are normalized to uppercase internally, so inconsistent casing from MediaPreserve (`a` vs `A`) does not produce duplicate columns.
- If a face has a preservation master but no access master (or vice versa), the missing columns are included in the output but left empty.
- Rows with no `<Original>` section will produce a warning and be skipped.

---

## OpenRefine workflow: filling metadata from TSV output

This workflow joins the TSV output from EmbedExtract into your existing tracking spreadsheet using barcode as the key column.

### Prerequisites

- OpenRefine 3.7+
- Your tracking spreadsheet (CSV or TSV) loaded as **Project A**
- The EmbedExtract TSV output loaded as **Project B**

---

### Step 1 — Load both files into OpenRefine

1. Open OpenRefine and click **Create Project**
2. Import your tracking spreadsheet (e.g. `p1201_SchoolofMusicDAT_Audio.csv`) → name it something like `DAT_tracking`
3. Create a second project from your EmbedExtract TSV output → name it something like `MediaPreserve_extracted`

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

For each field you want to pull from the TSV, add a new column in **DAT_tracking** using a GREL `cross()` expression.

1. In **DAT_tracking**, click the `barcode` column dropdown → **Edit column > Add column based on this column**
2. Name the new column to match your target field (e.g. `running time (mins)`)
3. Enter the GREL expression:

```
cell.cross("MediaPreserve_extracted", "barcode")[0].cells["running time mins"].value
```

Repeat for each field, changing the source column name in quotes each time. Key mappings between the TSV output and your tracking sheet:

| Tracking sheet column | EmbedExtract TSV column |
|---|---|
| `running time (mins)` | `running time mins` |
| `tape brand` | `stock brand` |
| `speed IPS` | `speed IPS` |
| `track configuration` | `track configuration` |
| `sound` | `sound` |
| `noise reduction` | `noise reduction` |
| `capture date` | `face a pres date created` |
| `digitizer` | `digitizer` |
| `digitizer notes` | `transfer comments` |

> **Note:** `capture date` and encoding chain fields come from the PreservationMaster section, so they use `face a pres` prefixed columns. If a tape has only one face, all data will be under face A.

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