# ingest   
A script for creating Meadow ingest sheets.

## Commands
`--input INPUT_PATH`, `-i INPUT_PATH`
    full path to input folder  
`--output OUTPUT_PATH`, `-o OUTPUT_PATH`
    full path to output csv file **(including name and extension)**. If not specified will use input directory  
`--load_inventory INVENTORY_PATH`, `-l INVENTORY_PATH`
    full path of inventory csv. If not specified the script will look in the input for inventories.   
`--skip`, `-s`
    Defines patterns to ignore. For example, `-s .mp3` would prevent the script from adding any .mp3 files it finds to the ingest sheet.   
`--description`, `-d`
    Use to specify column names to populate Meadow description field with. Can take multiple inputs. Information from each column will be separated by a ";" in the description. Example usage: `-d "Date/Time" "Barcode"`. If not specified, script will default to looking for the column "inventory_title"  
`--auxiliary`, `-x` Sets how to parse auxiliary files. Options include: `extension` (by extension; i.e. ".jpg"), `parse` (by word; i.e. "_Asset_Front"), `none` (no aux files). Default is `none`.   
`--prepend_accession`, `-p` Set a string to be added to the beginning of the file accession number when it is generated

## Usage

Basic
```
poetry run ingest -i INPUT_PATH
```

Using specified inventory.
```
poetry run ingest -i INPUT_PATH -l INVENTORY_PATH
```

Skip ".md5" files.
```
poetry run ingest -i INPUT_PATH -s .md5
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

## File Type Designations

**A** _am, -am, -a, _a, _am\_, -am-

**P** _pm, -pm, -p, _p, _pm\_, -pm-

**S** .framemd5, .xml, .json, .pdf, .xml.gz, .qctools.mkv, .log, .png, .PNG, dpx.txt

**X** .jpg, .jpeg, _Asset, -Asset, _Can, -Can, Front., Back., _Ephemera, -Ephemera

|File Type|File Role|
|:-------:|:-------:|
|-a or _a| A|
|-am or _am| A|
|-am- or _am\_| A|
|-Asset or _Asset|X|
|Back.| X|
|-can or _Can| X|
|dpx.txt|S|
|-Ephemera or _Ephemera| X|
|.framemd5| S|
|Front.|X|
|.json|S|
|.log|S|
|-p or _p|P|
|.pdf| S|
|-pm or _pm| P|
|-pm- or _pm\_| P|
|.png or .PNG| S|
|.qctool.mkv|S|
|.xml| S|
|.xml.gz| S|