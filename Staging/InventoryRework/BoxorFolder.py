import csv
import buildboxorFolderCSV
import savepath
import csvinput


def questions_boxorfolder():
    file_number = 1
    box_number = input("What is the box number?   ")
    folder_number = input("What is the folder number?    ")
    try:
        box_numberInt = int(box_number)
    except:
        print("Please enter an integer for box number")
        (quit)
    try:
        folder_numberInt = int(folder_number)
    except:
        print("Please enter an integer for folder number")
        quit()

    box_number = str(box_number).zfill(3)
    folder_number = str(folder_number).zfill(2)

    return box_number and folder_number


def box_or_folder(project_number, project_4letterID, box_number, folder_number):
    pages_yes_or_no = input("Are there multiple pages for your first work?    ")
    if pages_yes_or_no == "y":
        savepath.setFilename(project_number, project_4letterID)
        csv_filename = savepath.csv_file_name
        with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, csvinput.field_names)
            writer.writeheader()
            buildpageCSV.pages_yes(
                project_number,
                project_4letterID,
                box_number,
                folder_number,
            )
    else:
        number_of_files = input("How many works?    ")
        try:
            number_of_files = int(number_of_files)
        except:
            print("Please enter an integer for number of works")
            quit()

        while file_number <= number_of_files:
            file_number = str(file_number).zfill(2)
            buildboxorFolderCSV.build_boxOrFolder_inventory(
                project_number,
                project_4letterID,
                box_number,
                folder_number,
                file_number,
            )


def ask_newBoxorFolder(project_number, project_4letterID, box_number, folder_number):
    new_boxorfolder = input("Do you want to add a work - y for yes, n for no")

    if new_boxorfolder == "y":
        box_or_folder(project_number, project_4letterID, box_number, folder_number)
    elif new_boxorfolder == "n":
        savepath.setFilenameandSave(project_number, project_4letterID)
