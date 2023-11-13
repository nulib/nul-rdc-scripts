def build_boxOrFolder_inventory(
    project_number, project_4letterID, box_number, folder_number, file_number
):
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
            + file_number,
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
            + file_number
            + "_"
            + "0001"
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
            + file_number
            + "_"
            + "0001"
            + "_"
            + "a"
            + ".tif",
            "role": "A",
            "work_type": "IMAGE",
            "project_job_number": project_number,
            "container number ex. box number": box_number,
            "folder number": folder_number,
        }
    ]
    return inventory
