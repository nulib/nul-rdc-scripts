# Project Number Validation
def project_numbervalidation(project_number):
    project_number = project_number.lower()
    project_number_length = len(project_number)
    startswithTrue = project_numbervalidation_startswith(project_number)
    lengthTrue = project_numbervalidation_length(project_number_length)
    if startswithTrue and lengthTrue:
        project_number = project_number
    else:
        if startswithTrue:
            raise ValueError(
                "Please use a project number with 5 digits [including the p or j]"
            )
        elif lengthTrue:
            raise ValueError("Please start your project number with a p or a j")
    return project_number


def project_numbervalidation_length(project_number_length):
    try:
        project_number_lengthTrue = project_number_length == 5
    except:
        raise ValueError(
            "Please use a project number with 5 digits [including the p or j]"
        )
    return project_number_lengthTrue


def project_numbervalidation_startswith(project_number):
    try:
        project_number_startswithTrue = project_number.startswith(("p", "j"))
    except:
        raise ValueError("Please start your project number with a p or a j")
    return project_number_startswithTrue


# Project Letter Validation
def project_4letterID_validation(project_4letterID):
    project_4letterID = project_4letterID.lower()
    project_4letterID_length = len(project_4letterID)
    try:
        project_4letterID.isalpha()
        try:
            project_4letterID_length == 4
        except:
            raise ValueError("Please use 4 letters for your project ID")
    except:
        raise ValueError("Please use a project ID with letters only")
    return project_4letterID


def check_boxnumber(box_number):
    try:
        box_numberInt = int(box_number)
        box_number = str(box_number).zfill(3)
    except:
        raise TypeError("Please enter an integer for box number")
    return box_number


def check_foldernumber(folder_number):
    try:
        folder_numberINT = int(folder_number)
        folder_number = str(folder_number).zfill(2)
    except:
        raise TypeError("Please enter an integer for folder number")
    return folder_number


def check_numberworks(number_works):
    try:
        number_works = int(number_works)
    except:
        raise TypeError("Please enter an integer for number of works")
    return number_works


def check_worknumber(worknumber):
    try:
        worknumber = int(worknumber)
    except:
        raise TypeError("Please enter an integer for the work number")
    return worknumber


def check_pages(pages):
    try:
        pages = int(pages)
    except:
        raise TypeError("Please enter an integer for the number of pages")
    return pages
