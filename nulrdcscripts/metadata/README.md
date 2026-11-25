# General Information

Version Date: 4/27/2026

Document Owner: Quinn Sluzenski

Software Used: Command Line, Excel, Python

# Description
This scripts takes a Microsoft Excel export of a full inventory (all tabs included) and 1. convert each tab in the Excel file into individual csvs and 2. combines those csvs into a single csv that can be used for the metadata process. It combines the columns by title, not by position, so no adjustment is required beforehand even if columns have been rearranged.

## Usage
This script does not use poetry and must be called directly through the command line. In the command line, call the script name and the name of the Excel file you need to convert. It will create a directory in which all of the individual csvs, as well as the combined csv, are saved.

The names of the columns can be edited to adjust this script for other inventory formats.
