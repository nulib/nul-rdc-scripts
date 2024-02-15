import buildboxorFolderCSV
import csv
import inputvalidation
import pagePath
import setup
from csvinput import field_names as field_names


def BorFPath(project_number, project_4letterID, csvname):
    file_number = 1
    # Asks the box number
    box_number = setup.askbox_number()

    # Verifies the box number and sets ZFill -- change ZFill for different number of digits
    box_number = inputvalidation.check_boxnumber(box_number)

    # Asks the folder number
    folder_number = setup.askfolder_number()

    # Verifies the folder number and sets ZFill -- change ZFill for different number of digits
    folder_number = inputvalidation.check_foldernumber(folder_number)

    pages_yn = setup.ask_pages()

    if pages_yn == "y":
        pagePath.pageTrue(
            project_4letterID, project_number, box_number, folder_number, csvname
        )
    else:
        number_of_works = setup.ask_numberworks()  # number to loop by
        number_of_works = inputvalidation.check_numberworks(number_of_works)
        with open(csvname, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            file_number = int(file_number)
            while file_number <= number_of_works:
                file_number = str(file_number).zfill(2)
                inventory = buildboxorFolderCSV.build_boxOrFolder_inventory(
                    project_number,
                    project_4letterID,
                    box_number,
                    folder_number,
                    file_number,
                )
                for data in inventory:
                    writer.writerows(inventory)
                    file_number = int(file_number) + 1
    new_BorF = setup.ask_newBoxFolder()
    if new_BorF == "y":
        BorFPath(project_number, project_4letterID)
    elif new_BorF == "n":
        pass

    return inventory
