Version Date: 10/30/2023

Document Owner: Sophia Francis <br>

Software Used: Terminal or Command Prompt, VSCode (optional), QCTools (requires the output files not the software itself), Excel (or other CSV reader if accessing CSV file)

Packages required (also see .toml file): pandas, lxml, beautifulsoup4, tabulate, json, os, 

Description:<br>
This document provides information about running the QC Script and what information is required in order to do so.

## Important information:

If you are planning on running this in batch form (one folder with multiple xml files), make sure that if there are a mix of black and white videos and color videos, they are in separate folders and run separately to ensure the proper tests get run.


### _Regarding Summarization Stats from QCTools:_

Due to the nature of the summarization stats from the QCTools worksheet, these have been adapted so that they are less likely to incur skewing due to framecount (this concept has been communicated a developer of QCTools.) That being said, in order to see the documentation about how these numbers came to be see [this] (summarizationStats.md) document

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

### 5. Depending on what bitdepth you are utilizing, different values need to be used. To select:

- Use ```--10bit``` or ```-10``` for 10 Bit video

- Use ```--8bit``` or ```-8``` for 8 Bit Video

Adding to the example above, for a color video this would look like:

#### 10 Bit Video

```
run.py --input example.xml --color --10bit
```
```
run.py --input example.xml --color -10
```

#### 8 Bit Video

```
run.py --input example.xml --color --8bit
```
```
run.py --input example.xml --color -8
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