# Running the Script
## Running in Command Line
In the search bar of your computer search for Command Line

## Running in VSCode Terminal
## Running in VSCode Interactive Window


# Helpful Tips
In order to **_change the number of leading zeros_**, find zfill and change the number within the parenthese to how many digits you want the number to have. 

For example:
``` zfill(4)``` means that any number that you want to have leading zeros will always have to have 4 digits. So, 6 would become 0006; 14 would become 0014; 245 would become 0245; and 5462 would stay the same.


In order to **_change from inventorying access files to preservation files_**, find ```'role':'A'``` and replace it with ```'role':'P'```. After replacing that part, find ```file_number+''+'a'``` and replace it with ```file_number+''+'p'```


# Key to Variables


|Variable|Value|
|:--:|:--:|
|ask_new_work_bOrf|Asks whether or not you want to add a Box or a Folder to your project if you are running the Box/Folder option|
|ask_new_work_choose|Asks whether or not you want to add a new work if you are running the choose your own adventure option| 
|ask_new_work|Asks if you want to add a new work to the inventory|
|box_number|Based on user input for the box currently working on. Only shows for Box/Folder option.
|box_other|Asks whether or not you are using the box/folder designation or the choose your own adventure route|
|csv_name|Variable that sets the name of the CSV based on the user input|
|field_names|Gives the headers for each of the columns|
|file_number|Counts the number of the file that is being created by the script. Is incremented by one each time the loop runs|
|file_path|Variable for the location where you want to save the CSV file|
|folder_files|The total number of files to write. This provides the loop for 'x' number of times run this code|
|folder_number|Based on user input for the folder currently working on|
|new_bOrf|Asks whether or not you want to add a new box or folder|
|new_work|Asks whether or not your want to add a new work|
|os.system|Calls the os.system of your computer -- this is how it knows to open Excel|
|page_number|Counts number of pages (similar to file_number). Increments up by one after each loop. Only shows when running the choose your adventure route|
|pages|Based on user input for the page currently working on. Only shows when running the choose your own adventure route|
|pages_yn|Asks whether or not you want to add a work that uses page designations|
|proj_number|Project Number (ex. p0386)|


