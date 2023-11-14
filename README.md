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
[Meadow Ingest Sheet Generator - ingest](/nulrdcscripts/ingest/)   

### Inventorying:
[Inventory Creator for Image and Text Works - inventory](/nulrdcscripts/inventory/)   

### Deprecated

[dpx2ffv1 Film Transcoder - fproc](/nulrdcscripts/fproc/)   
[Meadow Image CSV Converter - text](/nulrdcscripts/text/)   

## Poetry Setup

Install poetry with the following command.
```
curl -sSL https://install.python-poetry.org | python3 -
```
**Windows**: after it installs, it will list the install directory in the terminal as `Actual Location`. Copy this path up to the `Scripts` folder and run the following command to add it to your system path.  
```
setx path "%path%;C:\poetry\path\up\to\Scripts\"
```
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