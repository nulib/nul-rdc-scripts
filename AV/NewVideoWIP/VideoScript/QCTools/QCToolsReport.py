import subprocess
from VideoScript.Arguments.Arguments import args

def generate_qctools(input):
    qctools_args=[args.qcli_path, '-i', input]
    subprocess.run(qctools_args)
