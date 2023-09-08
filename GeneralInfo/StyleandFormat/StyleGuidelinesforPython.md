Version date: 09/06/2023

Document owner: SF

Examples from PEP8

# Below are the standards that we will be using for our Python Scripts

### Layout
* Use 4 spaces as indentation
* No mixing tabs and spaces! Only use spaces or a tab that converts to spaces
* Max characters per line = 79
* Wrapped elements should be vertically aligned
    * Unless they are an extended if statement. Then use additional indentation
* Use implied line continuation inside parantheses
* Blank lines
  * Top Level & Class - surround with 2 blank lines
  * Method definitions - surround with 1 blank line
  * Between groups - surround with 1 blank line
  * Otherwise do NOT use blank lines
* Use UTF-8 encoding

### Imports
* Each import should be on a separate line
* Listed after module comments and before module globals and module constants
* Group imports
  1. Standard library imports
  2. Related third party imports
  3. Local application/library specific imports
* Blank line between each group
* Absolute only
* No wildcard imports
* 

### Naming Conventions (These are ideals.)
* Functions
	* Lowercase separate words with underscore between words
* Variables
	* Lowercase, words separated with underscore
* Class
	* Start with capital letter. No underscores
* Method 
	* Lowercase separates with underscores
* Constant
	* Uppercase and separate with underscores
* Modules
	* Short lowercase words separated with underscores
* Package
	* Short lowercase words separated. No underscores.

*HOWEVER, if you have anything with an abbreviation, capitalize the whole abbreviation

#### Resources:

##### Auto PEP8 Compliance in VSCode: 
* Extensions
	* AutoPep8
	* Yapf
	* Black

* Packages that check PEP8 compliance
	* PyCodeStyle 
	* Flake 8

