import subprocess


def main(software):
    """This will check if the software is installed on the computer in use"""
    dashVersion = ["ffprobe", "ffplay", "ffmpeg", "qcli"]
    doubleDashVersion = ["sox", "mediaconch", "bwfmetaedit"]

    if software in dashVersion:
        versionCommand = "-version"
    elif software in doubleDashVersion:
        versionCommand = "--version"
    else:
        print("This software is not included in this checking tool")

    try:
        command = software + " " + versionCommand
        subprocess.run(command)
    except:
        raise Exception(software, "cannot be found. Check your path variable.")
