import os
import pandas as pd
import glob
import click


def file_split(file):
    # Split the file into name and extension
    s = file.split('.')
    name = '.'.join(s[:-1])  # get directory name without extension
    return name


def getsheets(inputfile):
    # Create the directory to store CSVs
    name = file_split(inputfile)
    try:
        os.makedirs(name)
    except FileExistsError:
        pass

    df1 = pd.ExcelFile(inputfile)
    for x in df1.sheet_names:
        print(x + '.csv', 'Done!')
        df2 = pd.read_excel(inputfile, sheet_name=x)
        filename = os.path.join(name, x + '.csv')
        df2.to_csv(filename, index=False)
    print('\nAll Done!')
    return name  # Return the folder name with CSVs


def combine_csvs_from_folder(folder_path):
    dfs = []

    # Find all CSV files in the specified folder
    for csv_file in sorted(glob.glob(os.path.join(folder_path, '*.csv'))):
        # Read CSV, skipping the first row, letting the second row be the header
        df = pd.read_csv(csv_file, skiprows=1)

        # Clean up column names (strip whitespace, remove line breaks)
        df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('\r', '').str.replace('\\n', ' ')

        # Define the expected columns and how to rename them
        expected_cols = {
            'work_accession_number': 'work_accession_number',
            'file_accession_number': 'file_accession_number',
            'filename': 'filename',
            'label': 'label',
            'description': 'description',
            'Checked in? (yes/no)': 'Checked in? (yes/no)',
            'Packing & Shipping Check in? (yes/no)': 'Packing & Shipping Check in? (yes/no)',
            'Capture date': 'Capture date',
            'Staff Initials': 'Staff Initials',
            'Container number (ex. Box and folder number)': 'Container number (ex. Box and folder number)',
            'folder number': 'folder number',
            'Width (cm.)': 'Width (cm.)',
            'Height (cm.)': 'Height (cm.)',
            'Date (Year+Month+Day)': 'Date (Year+Month+Day)',
            'project_job_number': 'project_job_number',
            'Notes about album page or photo': 'Notes about album page or photo',
            'Production Notes For shipping/receiving info see SharePoint': 'Production Notes For shipping/receiving info see SharePoint'
        }

        # Filter and rename only if the columns exist
        existing = {k: v for k, v in expected_cols.items() if k in df.columns}
        df = df[list(existing.keys())].rename(columns=existing)

        dfs.append(df)

    # Combine all cleaned DataFrames
    final_df = pd.concat(dfs, ignore_index=True)

    # Save the combined data
    combined_filename = os.path.join(folder_path, 'combinedinventory.csv')
    final_df.to_csv(combined_filename, index=False)

    print(f"Combined CSV saved to: {combined_filename}")
    return combined_filename


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('inputfile')
def combine(inputfile):
    # Step 1: Split Excel sheets into CSVs
    folder = getsheets(inputfile)

    # Step 2: Combine the CSVs into one
    combine_csvs_from_folder(folder)


if __name__ == "__main__":
    combine()
    
