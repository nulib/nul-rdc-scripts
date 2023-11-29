import setup
import inputvalidation
import csv
import BorF


def pageTrue(project_number, project_4letterID, box_number, folder_number, csvname):
    """
    If you use this route the loop will increment for pages and lead to a request for additional works at the end.
    """
    file = setup.ask_worknumber
    pages = setup.ask_pages  # number to loop by
    pages = inputvalidation.checkpages(pages)
    page_number = 1
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
            csv.writer.writerows(inventory)
            page_number = int(page_number) + 1
    new_work = setup.ask_newwork()
    if new_work == "y":
        pageTrue(project_number, project_4letterID, box_number, folder_number, csvname)
    else:
        new_BorF = setup.ask_newBoxFolder()
        if new_BorF == "y":
            BorF.BorFPath(project_number, project_4letterID, csvname)
        elif new_BorF == "n":
            pass

    return inventory
