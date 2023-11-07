import buildboxorFolderCSV
import csv
import inputvalidation
import pagePath
import setupquestions


def BorFPath(project_number, project_4lettID):
    file_number = 1
    # Asks the box number
    box_number = setupquestions.askbox_number()

    # Verifies the box number and sets ZFill -- change ZFill for different number of digits
    box_number = inputvalidation.check_boxnumber(box_number)

    # Asks the folder number
    folder_number = setupquestions.askfolder_number()

    # Verifies the folder number and sets ZFill -- change ZFill for different number of digits
    folder_number = inputvalidation.check_foldernumber(folder_number)

    pages_yn = setupquestions.ask_pages()

    if pages_yn == "y":
        pagePath.pageTrue(project_4lettID, project_number, box_number, folder_number)
    else:
        number_of_works = input("How many works?    ")
        try:
            number_of_works = int(number_of_works)
        except:
            raise ("Please enter an integer for number of works")

        while file_number <= number_of_works:
            file_number = str(file_number).zfill(2)
            inventory = buildboxorFolderCSV.build_boxOrFolder_inventory(
                project_number,
                project_4lettID,
                box_number,
                folder_number,
                file_number,
            )
        for data in inventory:
            csv.writer.writerows(inventory)
            file_number = int(file_number) + 1
    new_BorF = setupquestions.ask_newBoxFolder()
    new_BorF = new_BorF.lower()
    if new_BorF == "y":
        BorFPath(project_number, project_4lettID)
    elif new_BorF == "n":
        pass

    return inventory
