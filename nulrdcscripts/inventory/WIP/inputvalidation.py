def project_numbervalidation_starts(project_number):
    try:
        project_number.startswith("P")
    except:
        try:
            project_number.startswith("J")
        except:
            print("Please start your project number with a P or a J")
            quit()


def project_numbervalidation_length(project_number):
    project_number_length = len(project_number)
    try:
        project_number_length == 5
    except:
        print("Please answer with a 4 digit number following P or J")
        quit()


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
