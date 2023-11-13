import os


csv_file_name = ""


def setFilename(project_number, project_4letterID):
    csv_file_name = (
        project_number + "_" + project_4letterID + "_" + "inventory" + ".csv"
    )
    return csv_file_name


def opencsv(csv_file_name):
    open_CSV = "" + "start EXCEL.exe" + "" + csv_file_name
    os.system(open_CSV)
