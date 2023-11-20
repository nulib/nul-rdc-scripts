import BorF
import choose
import saveCSV
import setup
import inputvalidation

# Gets user input and validates for Project Number
project_number = setup.ask_projnum()
project_number = inputvalidation.project_numbervalidation(project_number)

# Gets user input and validates for Project 4 Letter ID
project_4letterID = setup.ask_4letterID()
project_4letterID = inputvalidation.project_4letterID_validation(project_4letterID)

# Sets the filename for the CSV file
csvname = setup.setFilename(project_number, project_4letterID)

# Gets user input about box or folder. Ensures the answer is lowercase
box_other = setup.boxor_other()
box_other = box_other.lower()

# Uses input from above to run a distinct path
if box_other == "y":
    inventory = BorF.BorFPath(project_number, project_4letterID, csvname)
elif box_other == "n":
    inventory = choose.choosePath(project_number, project_4letterID, csvname)

saveCSV.opencsv(csvname)
