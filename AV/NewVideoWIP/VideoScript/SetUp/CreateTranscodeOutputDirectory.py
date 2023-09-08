import os


def create_transcode_output_folders(baseOutput, outputFolderList):
    if not os.path.isdir(baseOutput):
        try:
            os.mkdir(baseOutput)
        except:
            print("Unable to create output folder:", baseOutput)
    else:
        print(baseOutput, "already exists")
        print("Proceeding")
    for folder in outputFolderList:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except:
                print("Unable to create output folder:", folder)
        else:
            print("Using existing folder", folder, "as output")
