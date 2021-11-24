# Meadow CSV Script <br/>
This is a Python script for creating ingest sheets that are ready for Meadow. Run the script on a CSV file or folder containing multiple CSV files for a single project and it will produce a new CSV file containing only the columns necessary for ingesting files into Meadow. If run on a folder of CSV files, the script will merge them into a single CSV file.

### Commands <br/>
**-i**, **--input**   This should be the full path to a CSV file or folder containing multiple CSV files. <br/>
**-o**, **--output**   This should be the full path, including file name, to a csv file for writing an output CSV to. If the output already exists it will be overwritten. Example - /user/my_documents/my_csv_file.csv <br/>

### Dependencies - CHECK BEFORE TRYING TO RUN THE SCRIPT <br/>
- Before running the command you will need a recent version of Python installed. <br/>
- Install python from the Python website if it is not already installed. If you aren't sure whether or not python is installed, try typing `python -h` in the command line. If installing Python on Windows make sure to check the box to add python to your PATH during installation. <br/>

### Usage <br/>
- Run the Command using the run.py script located in pandas_testing/image_processing <br/>
- You may need to make the script executable first. In order to do so, type `chmod 755` into the command line on a mac followed by a space, then drag and drop the run.py file into the command line and press return. The full command should look something like `chmod 755 path/to/git/folder/pandas_testing/image_processing/run.py` <br/>
- You can check if the script is executable by trying to bring up the help text `run.py -h` <br/>
- Once the script is executable, you can run it by setting the correct inputs and outputs. The structure of the command should be: [full path to run.py file] [space] [-i] [space] [full path to input CSV or folder] [space] [-o] [space] [full path to output CSV file]
-This should look like: `path/to/git/folder/pandas_testing/image_processing/run.py -i path/to/input/folder -o path/to/csv/mycsv.csv` <br/>
