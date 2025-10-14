# Save script in a folder with all of the inventory sheets you need to combine

import csv
import pandas as pd
import glob

dfs = []

for csv_file in sorted(glob.glob('*.csv')):
    # Read CSV, skipping the first row, letting the second row be the header
    df = pd.read_csv(csv_file, skiprows=1)

    # Clean up column names (strip whitespace, remove line breaks)
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('\r', '').str.replace('\\n', ' ')

    # Define the expected columns and how to rename them. Edit to add the names of more columns if you need them.
    expected_cols = {
        'work_accession_number': 'work_accession_number',
        'filename': 'filename',
        'description': 'description',
        'Container number ex. Box number': 'Box',
        'Width (cm.)': 'Width',
        'Height (cm.)': 'Height',
        'Date (Year+Month+Day)': 'Date',
        'Notes about album page or photo': 'Notes',
    }

    # Filter and rename only if the columns exist
    existing = {k: v for k, v in expected_cols.items() if k in df.columns}
    df = df[list(existing.keys())].rename(columns=existing)

    dfs.append(df)

# Combine all cleaned DataFrames
final_df = pd.concat(dfs, ignore_index=True)

# Save the combined data
final_df.to_csv('combinedinventory.csv', index=False)