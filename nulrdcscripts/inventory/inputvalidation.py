# Project Number Validation
def project_number_validation(project_number):
    """
    Checks that the project number starts with either a p or a j and that it is exactly 5 characters
    """
    project_number_length = len(project_number)
    project_number
    project_number_first_char = project_number.startswith(("p", "j"))

    check_projectnumber_len(project_number_length)
    check_projectnumber_firstchar(project_number_first_char)


def check_projectnumber_firstchar(project_number_first_char):
    """
    Checks the first character of the project number
    """
    if project_number_first_char:
        pass
    else:
        raise ValueError("Project number must start with a p or a j")


def check_projectnumber_len(project_number_length):
    """
    Checks the length of the project number.
    """
    if project_number_length == 5:
        pass
    else:
        raise ValueError("Project number must be 5 characters long")


# Project Letter Validation
def project_4letterID_validation(project_4letterID):
    """
    Checks that the 4 letter ID is only alphabetical and that there are only 4 characters
    """
    length_4letterID = len(project_4letterID)
    alpha_4letterID = project_4letterID.isalpha()
    check_alpha_4letterID(alpha_4letterID)
    check_length_4letterID(length_4letterID)


def check_length_4letterID(length_4letterID):
    """
    Checks the length of the 4 character ID
    """
    if length_4letterID == 4:
        pass
    else:
        raise ValueError("4 Letter ID must be only 4 characters")


def check_alpha_4letterID(alpha_4letterID):
    """'
    Checks that the 4 characters are all alphabetical
    """
    if alpha_4letterID:
        pass
    else:
        raise ValueError("4 Letter ID must be all letters")


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
