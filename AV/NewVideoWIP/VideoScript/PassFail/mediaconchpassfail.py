import subprocess
from VideoScript.SetUp.Arguments import args


def mediaconch_policy_check(input, policy):
    mediaconchResults = (
        subprocess.check_output([args.mediaconch_path, "--policy=" + policy, input])
        .decode("ascii")
        .rstrip()
        .split()[0]
    )
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults
