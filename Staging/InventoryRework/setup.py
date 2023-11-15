# Questions


def ask_projnum():
    project_number = input("What is the project number?    ")
    return project_number


def ask_4letterID():
    project_4letterID = input("What is your projects 4 letter ID?    ")
    return project_4letterID


def askbox_number():
    box_number = input("What is the box number?    ")
    return box_number


def boxor_other():
    box_other = input("Are there boxes and folders? y for Yes and n for No     ")
    box_other = box_other.lower()
    return box_other


def ask_numberworks():
    numberworks = input("What is the number of works?   ")
    return numberworks


def askfolder_number():
    folder_number = input("What is the folder number?    ")
    return folder_number


def ask_worknumber():
    worknumber = input("What is the work number?   ")
    return worknumber


def ask_pages():
    pages_yn = input(
        "Are there multiple pages for your first work?    y for Yes and n for No"
    )
    pages_yn = pages_yn.lower()
    return pages_yn


def ask_newBoxFolder():
    new_boxFolder = input("Do you want to add a new work - y for yes, n for no")
    new_boxFolder = new_boxFolder.lower()
    return new_boxFolder


def ask_workinfo():
    workinfo = input("What is your work info (ex. v0001)?")
    return workinfo


# Setting file name


def setFilename(project_number, project_4letterID):
    csv_file_name = (
        project_number + "_" + project_4letterID + "_" + "inventory" + ".csv"
    )
    return csv_file_name
