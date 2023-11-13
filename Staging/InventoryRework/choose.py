import inputvalidation
import setupquestions
import csv
import savepath
import csvinput 

def chooseYourOwnAdventure(project_number, project_4letterID):
    workinfo = setupquestions.ask_workinfo()
    number_works = setupquestions.ask_numberworks()
    inputvalidation.check_numberworks(number_works)
    field_names = csvinput.field_names
    file_number = 1
    csv_name = savepath.setFilename(project_number, project_4letterID)

    with open(csv_name, "a", newline="", encoding="utf-8") as csvfile:
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

        