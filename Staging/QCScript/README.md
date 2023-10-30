Version Date: 10/30/2023

Document Owner: Sophia Francis <br>

Software Used: Terminal or Command Prompt, VSCode (optional), QCTools (requires the output files not the software itself), Excel (or other CSV reader if accessing CSV file)

Packages required (also see .toml file): pandas, lxml, beautifulsoup4, tabulate, json, os

Description:<br>
This document provides information about running the QC Script and what information is required in order to do so.

## Important information:

If you are planning on running this in batch form (one folder with multiple xml files), make sure that if there are a mix of black and white videos and color videos, they are in separate folders and run separately to ensure the proper tests get run.

## Running with Parser (still in development - not functional):

### 1. Drag and drop the run.py file into the terminal
### 2. Locate your file or file folder path:

For this example I will be using:
- example.xml as the file version
- /files/example.xml as the filepath version

### 3. Type --input or -i (they do the same thing) followed by your file or folder path

```
run.py --input example.xml
```
```
run.py -i /files/example.xml
```
### 4. Depending on whether or not you are running a black and white video or a color video, different processes should be run. To select:
- Use ```--blackwhite```  or ```-bw``` for black and white video
- Use ```--color``` or ```-c``` for color video

Adding to the first example in step 3, these options would look like this:

#### Black and white video

```
run.py --input example.xml --blackandwhite
```
```
run.py --input example.xml -bw
```

#### Color video

```
run.py --input example.xml --color
```
```
run.py --input example.xml -c
```






## Contributers:

Alec Bertoy

Dan Zellner

Morgan Morel

Brendan Coates

Ben Turkus
