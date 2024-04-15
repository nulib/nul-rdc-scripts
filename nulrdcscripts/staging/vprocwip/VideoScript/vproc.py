import sys
from nulrdcscripts.staging.vprocwip import setup

if sys.version_info[0] < 3:
    raise Exception("Python 3 or higher is required")


def main():
    indir = setup.input_check()
    outdir = setup.output_check()
    # Sets the paths for the softwares to check
    ffmpeg_path = setup.set_path("ffmpeg")
    mediaconch_path = setup.set_path("mediaconch")
    ffprobe_path = setup.set_path("ffprobe")
    # Checks if these paths exist
    setup.exists(ffmpeg_path)
    setup.exists(mediaconch_path)
    setup.exists(ffprobe_path)
    # Checks that the mixdown provided (optional) is valid
    setup.checkmixdown()
    basefilename = setup.basefilename()
