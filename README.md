# nul-rdc-scripts
Scripts used by the RDC Digitization Team.   

## Poetry Setup

Install poetry with the following command.
```
curl -sSL https://install.python-poetry.org | python3 -
```
After it installs, it will say in the command line where poetry was installed. **Manually add this folder to your path (if on Windows) and reopen terminal.**  
In the terminal, `cd` to repository parent folder (nul-rdc-scripts) and run `poetry install`

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