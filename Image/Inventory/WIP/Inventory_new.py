import os
import csv
import inputvalidation
import BoxorFolder
import savepath
import buildchoose
# Asking the user questions to decide the workflow that is going to be used by the script
project_number = input("What is the project number?    ")

inputvalidation.project_numbervalidation_starts(project_number)
inputvalidation.project_numbervalidation_length(project_number)


project_4letterID = input("What is the four letter ID?    ")

inputvalidation.project_4letterID_validation(project_4letterID)

box_other = input("Are there boxes and folders? y for Yes and n for No     ")

file_path = input("Where do you want to save to?   ")

if box_other == "y":
    BoxorFolder.box_or_folder(project_number, project_4letterID)

elif box_other == "n":
    buildchoose.choosepath(project_number, project_4letterID)

savepath.setFilenameandSave(project_number, project_4letterID)


def ask_new_work_bOrf():
    new_work = input(
        "Do you want to add a new work - y for yes, n for no which will open the CSV   "
    )

    if new_work == "y":  # if you want a new work this will run
        file_number = 1
        work_info = input("What is the work info?    ")
        number_files = int(input("How many works?   "))  # number to loop by
        while (
            file_number <= number_files
        ):  # runs while the file number is less than or equal to the number of files that you need
            # Leading Zeros
            file_number = str(file_number).zfill(4)
            # Leading Zeros

            # Combines the information that the user has put in to fill out select fields in the CSV file
            inventory = [
                {
                    "work_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info,
                    "file_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info
                    + "_"
                    + file_number
                    + "_"
                    + "a",
                    "filename": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info
                    + "_"
                    + file_number
                    + "_"
                    + "a"
                    + ".tif",
                    "role": "A",
                    "work_type": "IMAGE",
                    "project_job_number": project_number,
                }
            ]
            for data in inventory:
                writer.writerows(inventory)
                # Below increments the row and file up by one
                file_number = int(file_number) + 1

                ask_new_work_bOrf()

    elif new_work == "n":
        save_CSV()  # command to save the CSV
        os.system(open_CSV)  # Command to open the CSV in Excel


def ask_new_work_choose():
    new_work = input(
        "Do you want to add a new work - y for yes, n for no which will open the CSV   "
    )

    if new_work == "y":  # if you want a new work this will run
        file_number = 1
        work_info = input("What is the work info?    ")
        number_files = int(input("How many works?   "))  # number to loop by
        while (
            file_number <= number_files
        ):  # runs while the file number is less than or equal to the number of files that you need
            # Leading Zeros
            file_number = str(file_number).zfill(4)
            # Leading Zeros

            # Combines the information that the user has put in to fill out select fields in the CSV file
            inventory = [
                {
                    "work_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info,
                    "file_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info
                    + "_"
                    + file_number
                    + "_"
                    + "a",
                    "filename": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + work_info
                    + "_"
                    + file_number
                    + "_"
                    + "a"
                    + ".tif",
                    "role": "A",
                    "work_type": "IMAGE",
                    "project_job_number": project_number,
                }
            ]
            for data in inventory:
                writer.writerows(inventory)
                # Below increments the row and file up by one
                file_number = int(file_number) + 1

        ask_new_work_choose()
    elif new_work == "n":
        save_CSV()  # Saves the CSV File
        os.system(open_CSV)  # Opens the CSV file in Excel

    elif new_bOrf == "n":  # if you do not want to run a new box or folder
        new_pages = input(
            "Do you want to add a work with more than one page - y for Yes and n for No    "
        )  # will ask if you want to add a work that has to have page designation
        if new_pages == "y":  # if you want to use page designation this will run
            page_path()
        elif new_pages == "n":
            save_CSV()  # Saves the CSV
            os.system(open_CSV)  # Opens the CSV in Excel


def page_path():  # This script runs when you want to add works with page designations
    page_number = 1
    box_number = input("What is the box number?    ")
    folder_number = input("What is the folder number?   ")

    # Leading Zeros
    box_number = str(box_number).zfill(3)
    folder_number = str(folder_number).zfill(2)
    # Leading Zeros

    file = input("What is your work number?   ")
    pages = int(
        input("What is the number of images in the work?     ")
    )  # number to loop by

    while (
        page_number <= pages
    ):  # runs while the file number is less than or equal to the number of files that you need
        # Leading Zeros
        page_number = str(page_number).zfill(4)
        file = str(file).zfill(2)
        # Leading Zeros

        inventory = [
            {
                "work_accession_number": project_number
                + "_"
                + project_4letterID
                + "_"
                + "b"
                + box_number
                + "_"
                + "f"
                + folder_number
                + "_"
                + file,
                "file_accession_number": project_number
                + "_"
                + project_4letterID
                + "_"
                + "b"
                + box_number
                + "_"
                + "f"
                + folder_number
                + "_"
                + file
                + "_"
                + page_number
                + "_"
                + "a",
                "filename": project_number
                + "_"
                + project_4letterID
                + "_"
                + "b"
                + box_number
                + "_"
                + "f"
                + folder_number
                + "_"
                + file
                + "_"
                + page_number
                + "_"
                + "a"
                + ".tif",
                "Container number ex. Box Number": box_number,
                "folder number": folder_number,
                "role": "A",
                "work_type": "IMAGE",
                "project_job_number": project_number,
            }
        ]

        for data in inventory:
            writer.writerows(inventory)
            page_number = int(page_number) + 1
    ask_new_bOrf()  # will then call the ask_new_bOrf function to see if you want to add a box or folder next. If you want to run another work with page designations, answer 'n' to the first question and the 'y' to the next


# setting variables up to be used




else:
    print("Try again running the script again with y for YES or n for NO")
