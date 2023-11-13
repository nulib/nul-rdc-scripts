import QcilCheck
import FFMPEGCheck
import FFProbeCheck
import MediaConchCheck
from Arguments import args

if not args.skip_qcli:
    QcilCheck.qcli_check()
MediaConchCheck.mediaconch_check()
FFProbeCheck.ffprobe_check()
ffvers = FFMPEGCheck.get_ffmpeg_version()
