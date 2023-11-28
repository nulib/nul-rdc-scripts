import inputvalidation
import setup
import csv
import csvinput


def chooseYourOwnAdventure(project_number, project_4letterID, csvname):
    """
    Lets you have a more flexible filenaming structure. Primarily used for legacy projects. This is an optional path that is only used if you enter 'n' for box/folder question.
    """
    workinfo = setup.ask_workinfo()
    number_works = setup.ask_numberworks()
    inputvalidation.check_numberworks(number_works)
    field_names = csvinput.field_names
    file_number = 1

    with open(csvname, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        while (
            file_number <= number_works
        ):  # runs while the file number is less than or equal to the number of files that you need
            # leading zeros
            file_number = str(file_number).zfill(4)
            # leading zeros

            inventory = [
                {
                    "work_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + workinfo,
                    "file_accession_number": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + workinfo
                    + "_"
                    + file_number
                    + "_"
                    + "a",
                    "filename": project_number
                    + "_"
                    + project_4letterID
                    + "_"
                    + workinfo
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
