# Image-Processing <br/>
Scripts for running various automated QC functions on image projects.

## INSTRUCTIONS FOR TESTING <br/>

### Commands <br/>
**-i**, **--input**   This should be the full path to a project folder. If one or more inventory csv files are placed in the base folder of your input and you do not use the `--inventory` command to specify a different csv file or directory, those inventories will be used for processing the files. <br/>
**-o**, **--output**   This should be the full path, including file name, to a csv file for writing an output csv to. If the output already exists it will be overwritten. Example - /user/my_documents/my_csv.csv <br/>
**--exiftool**  Used to specify a custom path to ExifTool. This should generally not be needed. <br/>
**--inventory**   This should be the full path to a folder containing inventory csv files. Inventories should be left in their original formatting at the moment. If the folder contains multiple inventories the script will try to combine them. <br/>
**--verify_checksums**  This will try to verify existing checksums. It should be followed by the specific type of checksum file to verify (i.e. `--verify_checksums md5` or `--verify_checksums md5 sha1`). Currently the only supported formats are `md5` and `sha1`. Checksum files are expected to end with the specified text (sha1 files should end with .sha1). <br/>
**--verify_metadata**  This will run ExifTool on each TIFF file and check whether the IPTC fields By-line, Headline, Source, and CopyrightNotice match the listed information in the inventory (the Creator, Headline, Source, and Copyright Notice columns). By default this command will only check if the inventory field contains the text found in the file so that truncated metadata will also be matched (i.e. a file with IPTC metadata "Northwestern Uni" would pass even if the inventory metadata is "Northwestern University"). <br/>
**--strict**  When used with `--verify_metadata` this enforces exact matches when checking metadata (i.e. a file with IPTC metadata "Northwestern Uni" would fail if the inventory metadata is "Northwestern University"). <br/>

### Dependencies - CHECK BEFORE TRYING TO RUN THE SCRIPT <br/>
- Before running the command you will need a recent version of Python, the Pandas and Pillow modules, and Exiftool installed. <br/>
- Install python from the Python website if it is not already installed. If you aren't sure whether or not python is installed, try typing `python -h` in the command line. If installing Python on Windows make sure to check the box to add python to your PATH during installation. <br/>
- You can install Pandas module by typing `pip install pandas` in the command line when you have python installed (specifically install for python 3+ using `pip3 install pandas`).
- You can install Pillow using the command `python3 -m pip install --upgrade Pillow`
-ExifTool can be installed from the ExifTool website: https://exiftool.org/ 
-If on Windows, make sure that ExifTool is in your PATH or that you specify the path to the ExifTool executable using `--exiftool` when running the script. <br/>

### Usage <br/>
- Run the Command using the run.py script located in pandas_testing/image_processing <br/>
- You may need to make the script executable first. In order to do so, type `chmod 755` into the command line on a mac followed by a space, then drag and drop the run.py file into the command line and press return. The full command should look something like `chmod 755 path/to/git/folder/pandas_testing/image_processing/run.py` <br/>
- You can check if the script is executable by trying to bring up the help text `run.py -h` <br/>
- Once the script is executable, you can run it by setting the correct inputs and outputs: `path/to/git/folder/pandas_testing/image_processing/run.py -i path/to/input/folder -o path/to/csv/mycsv.csv --inventory path/to/inventory/folders` <br/>
- The commands can be included in any order as long as each is followed by the correct path (i.e. `--inventory` should always have the path to a csv file after it regardless of where it is in the command). <br/>

## Notes on changing script functionality <br/>
- Customizing the inventory column name used to match file names: Change the value of the column_to_match variable in the script <br/>
- Handle csv files with a second header row Change header=0 to header=1 <br/>

## Known Issues <br/>
