import subprocess
from nulrdcscripts.vproc.params import args


def mediaconch_implementation_check(input):
    mediaconchResults = (
        subprocess.check_output([args.mediaconch_path, input])
        .decode("ascii")
        .rstrip()
        .split()[0]
    )
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults


def qc_results(inventoryCheck, losslessCheck, mediaconchResults):
    QC_results = {}
    QC_results["QC"] = {
        "inventory check": inventoryCheck,
        "lossless check": losslessCheck,
        "mediaconch results": mediaconchResults,
    }
    return QC_results
