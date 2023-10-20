import csv
import BoxorFolder
import csvinput
import savepath

def bringinCSVFileName():
    savepath.setFilenameandSave(project_number, project_4letterID)
with open (, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, csvinput.field_names)
    writer.writeheader()


def pages_yes(
    project_number,
    project_4letterID,
    box_number,
    folder_number,
):
    filenumber = input("What is the work number?    ")

    try:
        filenumberint = int(filenumber)
    except:
        print("Please enter an integer for work number")

    page_number = 1
    pages = input("What is the number of images in the work?     ")

    try:
        pagesint = int(pages)
    except:
        print("Please use an integer for the number of pages")

    while (
        page_number <= pages
    ):  # runs while the file number is less than or equal to the number of files that you need
        # Leading Zeros
        page_number = str(page_number).zfill(4)
        filenumber = str(filenumber).zfill(2)
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
                + filenumber,
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
                + filenumber
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
                + filenumber
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

    BoxorFolder.ask_newBoxorFolder(project_number, project_4letterID)
