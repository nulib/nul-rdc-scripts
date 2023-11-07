def setFilename(project_number, project_4letterID):
    csv_file_name = (
        project_number + "_" + project_4letterID + "_" + "inventory" + ".csv"
    )
    return csv_file_name
