def project_numbervalidation(project_number):
    project_number = project_number.lower()
    try:
        project_number.startswith("p")
    except:
        try:
            project_number.startswith("j")
        except:
            raise ("Please start your project number with a p or a j")
    finally:
        project_number = project_numbervalidation_length(project_number)
        return project_number


def project_numbervalidation_length(project_number):
    project_number_length = len(project_number)
    try:
        project_number_length == 5
    except:
        raise ("Please answer with a 4 digit number following p or j")
    finally:
        return project_number


def project_4letterID_validation(project_4letterID):
    try:
        project_4letterID.isalpha()
    except:
        print("Please use a project ID with letters only")
        quit()
    project_4letterID_length = len(project_4letterID)
    try:
        project_4letterID_length == 4
    except:
        print("Please use 4 letters for your project ID")


def check_boxnumber(box_number):
    try:
        box_numberInt = int(box_number)
    except:
        print("Please enter an integer for box number")
        (quit)

    box_number = str(box_number).zfill(3)
    return box_number


def check_foldernumber(folder_number):
    try:
        folder_numberINT = int(folder_number)
    except:
        print("Please enter an integer for folder number")
        (quit)

    folder_number = str(box_number).zfill(2)
    return folder_number