def createchooseinventory(project_number, project_4letterID, file_number, work_info):
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
