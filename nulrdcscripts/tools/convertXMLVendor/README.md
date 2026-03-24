# EmbedExtract

Converts MediaPreserve XML delivery files into a flat TSV for OpenRefine processing. One row per barcode, with preservation and access master columns grouped side-by-side per face.

## Requirements

- Python 3.7+
- No external dependencies (standard library only)

## Usage

```bash
python embedextract.py -i <folder> [-o <output.tsv>]
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