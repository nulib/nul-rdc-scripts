Version Date: 7-1-25

Document Owner: Sophia Francis <br>

Software Used: Terminal or Command Prompt, VSCode (optional), QCTools (requires the output files not the software itself), Excel (or other CSV reader if accessing CSV file)

Packages required (also see .toml file): pandas, lxml, beautifulsoup4, tabulate, json, os, 

Description:<br>
This document provides information about running VidSleuth and what information is required in order to do so.

## Important information:

If you are planning on running this in batch form (one folder with multiple xml files), make sure that if there are a mix of black and white videos and color videos, they are in separate folders and run separately to ensure the proper tests get run.

### Changing Value ranges:
If you want to edit the value ranges that are used, then you can edit the CSVs Video8BitValues and Video10BitValues. However, caution must be used as these are used in equations throughout the script. I _do not_ recommend this.


## Running with Parser (still in development - not functional):

### 1. Drag and drop the run.py file into the terminal
### 2. Locate your file or file folder path:

For this example I will be using:
- example.xml as the file version
- /files/example.xml as the filepath version

### 3. Type --input or -i (they do the same thing) followed by your file or folder path

```
poetry run vids --input example.xml
```
```
poetry run vids -i /files/example.xml
```



## Many thanks to the contributers to this project:

Alec Bertoy

Dan Zellner

Morgan Morel

Brendan Coates

Ben Turkus

Dave Rice



## Some of the reference material utilized:

_Python for Data Analytics - Wes McKinney_ <br>
_Python Data Analytics: With Pandas, NumPy, and Matplotlib_ - Fabio Nelli <br>
_Practical Python Data Wrangling and Data Quality_ - Susan E. McGregor <br>
_Data Wrangling with Python_ - Jacqueline Kazil, Katharine Jarmul <br>
_How to convert an XML file to python pandas dataframe - reading xml with python_ - Paris Nakita Kejser - https://www.youtube.com/watch?v=WWgiRkvl1Ws&ab_channel=ParisNakitaKejser