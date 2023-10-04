import os
import shutil
from flatten.flatten_parameters import args

def main():

    indir = input_check()

    if args.mode == "single":
        single_flatten(indir)
    elif args.mode == "batch":
        batch_flatten(indir)
    else:
        print("Please enter 'single' or 'batch' for --mode")
        exit()
    


def input_check():
    """
    Checks if input was provided and if it is a directory that exists
    """
    if args.input_path:
        indir = args.input_path
    else:
        print("No input provided")
        quit()

    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    return indir

def single_flatten(folder):
    """
    performs flatten for single project
    """
    move(folder, folder)

def batch_flatten(folder):
    """
    performs flatten for folder containing multiple projects
    """
    for item in os.listdir(folder):
        # changes item's path to absolute
        item = os.path.join(folder, item)
        #performs flattens on item if its a folder
        if os.path.isdir(item):
            single_flatten(item)

def move(input, destination):
    """
    Recursively goes through file structure and moves files to destination
    """
    for item in os.listdir(input):
        # changes item's path to absolute
        item = os.path.join(input, item)
        # moves if item is file, calls move again if item is folder
        if os.path.isfile(item):
            if input != destination:
                try:
                    shutil.move(item, destination)
                except:
                    print(item + " could not be moved")
        else:
            move(os.path.join(input, item), destination)

    # deletes input folder if its not destination folder
    if input != destination:
        try:
            os.rmdir(input)
        except:
            print(input + " could not be deleted")