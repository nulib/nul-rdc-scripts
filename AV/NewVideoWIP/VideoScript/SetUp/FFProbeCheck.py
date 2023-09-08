import subprocess
from Arguments import args


def ffprobe_check():
    try:
        subprocess.check_output({args.ffprobe_path, "-version"}).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        print("Error locating FFProbe")
        quit()
