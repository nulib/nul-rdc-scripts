import BorF
import choose
import setupquestions
import inputvalidation

# Asks the project number
project_number = setupquestions.ask_projnum()

# Verifies the project number
project_number = inputvalidation.project_numbervalidation(project_number)

# Asks the 4 letter id
project_4lettID = setupquestions.ask_4lettID()

# Verifies the 4 letter id
project_4lettID = inputvalidation.project_4letterID_validation(project_4lettID)

box_other = setupquestions.boxor_other()
box_other = box_other.lower()

if box_other == "y":
    BorF.BorFPath(project_number, project_4lettID)

elif box_other == "n":
    choose.choosePath(project_number, project_4lettID)
