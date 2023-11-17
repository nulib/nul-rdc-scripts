# ingest   
A script for creating Meadow ingest sheets.

## Usage

In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.  

### Basic usage
```
poetry run ingest -i INPUT_PATH
```

### Using specified output
```
poetry run ingest -i INPUT_PATH -o OUTPUT_FILEPATH
```

### Using specified inventory
```
poetry run ingest -i INPUT_PATH -l INVENTORY_PATH
```

### Skip ".md5" files
```
poetry run ingest -i INPUT_PATH -s .md5
```

### Custom description
```
poetry run ingest -i INPUT_PATH -d "Date/Time" "Barcode"
```

### Parse x files by filename
```
poetry run ingest -i INPUT_PATH -x parse
```

### Example File Structure
```
input_folder
├── inventory.csv
├── item_1
│   └── item_1.mov
└── item_2
    └── item_2.mov
```

## Commands
`--input INPUT_PATH`, `-i INPUT_PATH`
    full path to input folder  
`--output OUTPUT_PATH`, `-o OUTPUT_PATH`
    full path to output csv file **(including name and extension)**. If not specified will use input directory  
`--load_inventory INVENTORY_PATH`, `-l INVENTORY_PATH`
    full path of inventory csv. If not specified the script will look in the input for inventories.   
`--skip`, `-s`
    Defines patterns to ignore. 
`--description`, `-d`
    Use to specify column names to populate Meadow description field with. Can take multiple inputs. If not specified, script will default to looking for the column "inventory_title"  
`--auxiliary`, `-x` Sets how to parse auxiliary files. Options include: `extension` (by extension; i.e. ".jpg"), `parse` (by word; i.e. "_Asset_Front"), `none` (no aux files). Default is `none`.   
`--prepend_accession`, `-p` Set a string to be added to the beginning of the file accession number when it is generated

## File Type Designations

|A|P|S|X|  
|:-------:|:-------:|:-------:|:-------:|  
|-a or _a|-p or _p|-s or _s|-x or _x|
|-am or _am|-pm or _pm|spectrogram|-Asset or _Asset|
|-am- or _am\_|-pm- or _pm\_|.json|Back.|
|||.log|-Can or _Can|
|||.pdf|-Ephemera or _Ephemera|
|||.xml|Front.|
|||.xml.gz|
|||.framemd5|
|||.qctool.mkv|
|||dpx.txt|

Anything that can't be identified will be set to 'S'

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