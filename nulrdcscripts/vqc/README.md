Version Date: 8-8-25

Document Owner: Sophia Francis <br>

Software Used: Terminal or Command Prompt, VSCode (optional), QCTools (requires the output files not the software itself), Excel (or other CSV reader if accessing CSV file), poetry

Packages required (also see .toml file): pandas, lxml, tabulate, json, os

Description:<br>
This document provides information about running MeduSight and what information is required in order to do so.

## Important information:


### Changing Value ranges:
If you want to edit the value ranges that are used, then you can edit the CSVs Video8BitValues and Video10BitValues. However, caution must be used as these are used in equations throughout the script. I _do not_ recommend this.


## Running CLI:

```
poetry run medu --input example.xml
```
```
poetry run medu -i /files/example.xml
```



## Many thanks to the contributers to this project:

Alec Bertoy

Dan Zellner

Sarah Hartzell

Morgan Morel

Brendan Coates

Ben Turkus





## Some of the reference material utilized:

_Python for Data Analytics - Wes McKinney_ <br>
_Python Data Analytics: With Pandas, NumPy, and Matplotlib_ - Fabio Nelli <br>
_Practical Python Data Wrangling and Data Quality_ - Susan E. McGregor <br>
_Data Wrangling with Python_ - Jacqueline Kazil, Katharine Jarmul <br>
_How to convert an XML file to python pandas dataframe - reading xml with python_ - Paris Nakita Kejser - https://www.youtube.com/watch?v=WWgiRkvl1Ws&ab_channel=ParisNakitaKejser