# ingest   
A script for creating Meadow ingest sheets for microfilm

## Usage

In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.  

### Basic usage
```
poetry run micro -i INPUT_PATH
```

### Using specified output
```
poetry run micro -i INPUT_PATH -o OUTPUT_FILEPATH
```

### Using specified inventory
```
poetry run micro -i INPUT_PATH -l INVENTORY_PATH
```


### Example File Structure
```
input_folder
├── inventory.csv
├── item_1
│   └── item_1
└── item_2
    └── item_2
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
`--prepend_accession`, `-p` Set a string to be added to the beginning of the file accession number when it is generated


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