import csv
import buildchooseCSV
import csvinput
import savepath


def choosepath(project_number, project_4letterID):
    work_info = input("What is your work info [ex. v for volume]?     ")
    number_files = input("What is the number of images?     ")

    try:
        number_filesINT = int(number_files)
    except:
        print("Please use an integer for the number of images in the work")

    file_number = 1
    with open(csv_name, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, csvinput.field_names)
        writer.writeheader()
        while file_number <= number_files:
            file_number = str(file_number).zfill(4)
            buildchooseCSV.createchooseinventory(
                project_number, project_4letterID, work_info
            )
    choosepath(project_number, project_4letterID)
