import subprocess
from Arguments import args


def qcli_check():
    try:
        subprocess.check_output(
            ([args.qcli_path, "-version"]).decode("ascii").rstrip().splitlines()[0]
        )
    except:
        print("Error locating qcli")
        quit()
