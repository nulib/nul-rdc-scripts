import BorF
import choose
import setup
import inputvalidation
import saveCSV

# Asks the project number
project_number = setup.ask_projnum()

# Verifies the project number
inputvalidation.project_number_validation(project_number)

# Asks the 4 letter id
project_4letterID = setup.ask_4letterID()

#  Verifies the 4 letter id
inputvalidation.project_4letterID_validation(project_4letterID)

csvname = setup.setFilename(project_number, project_4letterID)
box_other = setup.boxor_other()
box_other = box_other.lower()


def boxorother(box_other, project_number, project_4letterID, csvname):
    if box_other == "y":
        inventory = BorF.BorFPath(project_number, project_4letterID, csvname)

    elif box_other == "n":
        inventory = choose.choosePath(project_number, project_4letterID, csvname)
    return inventory


inventory = boxorother(box_other, project_number, project_4letterID, csvname)

saveCSV(inventory)
