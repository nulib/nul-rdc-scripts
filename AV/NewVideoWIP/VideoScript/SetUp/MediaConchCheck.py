import subprocess
from Arguments import args


def mediaconch_check():
    try:
        subprocess.check_output([args.mediaconch_path, "-v"]).decode(
            "ascii"
        ).rstrip().splitlines()[0]
    except:
        print("Error locating MediaConch")
        quit()
