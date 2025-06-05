# nul-rdc-scripts
Scripts used by the RDC Digitization Team.  

*Note: poetry is required for all scripts. See [Poetry Setup](#poetry-setup) to install poetry*

## Core Tools   

### Imaging Workflow:

[Image Quality Checker - iqc](/nulrdcscripts/iqc/)   

### AV Workflow:

[Video Processor - vproc](/nulrdcscripts/vproc)   
[Audio Processor - aproc](/nulrdcscripts/aproc)   

### Meadow

[Ingest MicroFilm - Meadow Ingest Sheet Generator for Microfilm - micro](/nulrdcscripts/ingestMicro/)   
[Ingest - Meadow Ingest Sheet Generator - ingest](/nulrdcscripts/ingest/)   

### Inventorying:
[Inventory Creator for Image and Text Works - inventory](/nulrdcscripts/inventory/)   

### Tools:
[MediaInfo Batch Generation](/nulrdcscripts/tools/EmbedExtract/)

[FFPlay Playback Window with Analysis Tools](/nulrdcscripts/tools/ffplaywindow/)

[Generate Access File - Video](/nulrdcscripts/tools/generateaccess/)

[Spectrogram Generation](/nulrdcscripts/tools/spectrogramgeneration/)

[]

### Text Workflow:
[PackagingScript](/nulrdcscripts/text) - Text Packaging Script


### Deprecated

[dpx2ffv1 Film Transcoder - fproc](/nulrdcscripts/fproc/)   
[Meadow Image CSV Converter - text](/nulrdcscripts/text/)   



## Poetry Setup

Install poetry with the following command.
```
curl -sSL https://install.python-poetry.org | python3 -
```
**Windows**: after it installs, it will list the install directory in the terminal as `Actual Location`. 
Copy this path up to the `Scripts` folder and add it to your path.  
**Note:** If you have an admin account, **add to System Path not User Path**  

Restart the terminal for this change to take effect.  
Finally in the terminal, [navigate](#terminal-help) to repository parent folder (nul-rdc-scripts) and run the following command 
```
poetry install
```

## Terminal help
Change directory with `cd FILEPATH`
- can be relative to current directory `cd folder`
- or absolute `cd C:\folder\subfolder`
- go back one folder with `cd ..`
- and return to your user folder with just `cd`  

See contents of current directory
- `dir` (WINDOWS)
- `ls` (LINUX)

Clear terminal
- `cls` (WINDOWS)
- `clear` (LINUX)
