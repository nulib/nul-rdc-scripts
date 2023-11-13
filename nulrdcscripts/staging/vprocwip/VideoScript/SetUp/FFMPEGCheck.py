import subprocess
from Arguments import args


def get_ffmpeg_version():
    ffmpeg_version = "ffmpeg"
    try:
        ffmpeg_version = (
            subprocess.check_output([args.ffmpeg_path, "-version"])
            .decode("ascii")
            .rstrip()
            .splitlines()[0]
            .split()[2]
        )
    except:
        print("Error getting FFMPEG Version")
        quit()
    return ffmpeg_version
