import progressbar
import os
import subprocess
from nulrdcscripts.tools.spectrogramgeneration.params import args


def generate_spectrogram(input_path, channels, output_path, spectroname, ffmpegpath):
    """Creates a spectrogram for each audio track in the input"""
    for index, item in enumerate(channels):
        spectrogram_resolution = "1928x1080"
        output = os.path.join(
            output_path, spectroname + "_spectrogram0" + str(index + 1) + "_s.png"
        )
        spectrogram_args = [ffmpegpath]
        spectrogram_args += ["-loglevel", "error", "-y"]
        spectrogram_args += ["-i", input_path, "-lavfi"]
        item = int(item)
        if item > 1:
            spectrogram_args += [
                "[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        else:
            spectrogram_args += [
                "[0:a:%(a)s]showspectrumpic=s=%(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        spectrogram_args += [output]
        subprocess.run(spectrogram_args)
        print("*** Spectrogram Generated ***")


def softwarecheck(software, softwarename):
    """Checks that software exists"""
    if "sox" in software:
        version = "--version"
    else:
        version = "-version"

    try:
        subprocess.check_output([software, version]).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        raise Exception("Cannot locate " + softwarename + ". Check path.")


def getnumberchannels(ffprobe_path, input_path):
    command = (
        ffprobe_path
        + " "
        + "-i"
        + " "
        + input_path
        + " "
        + "-show_entries stream=channels -select_streams a:0 -of compact=p=0:nk=1 -v 0"
    )
    output = subprocess.run(command, capture_output=True, text=True)
    channels = output.stdout
    channels = channels.replace("\n", "")
    return channels


def checkOrCreateOutput(output_path, input_path):
    if output_path == "NA":
        output_path = input_path
    else:
        pass

    outputdir = os.path.isdir(output_path)
    if outputdir:
        pass
    else:
        output_path = os.path.dirname(output_path)
    return output_path


def callableSpectrogram(ffprobe_path, input_path, output_path):
    channels = getnumberchannels(ffprobe_path, input_path)
    spectroname, ext = os.path.splitext(os.path.basename(input_path))
    generate_spectrogram(input_path, channels, output_path, spectroname)


def main():
    """Only runs if you are running this command on it's own"""
    input_path = os.path.abspath(args.input_path)
    ffprobe_path = args.ffprobe_path
    ffmpeg_path = args.ffmpeg_path
    sox_path = args.sox_path
    softwarecheck(sox_path, "sox")
    softwarecheck(ffprobe_path, "ffprobe")
    softwarecheck(ffmpeg_path, "ffmpeg")
    channels = getnumberchannels(ffprobe_path, input_path)
    output_path = args.output_path
    output_path = checkOrCreateOutput(output_path, input_path)
    spectroname, ext = os.path.splitext(os.path.basename(input_path))
    generate_spectrogram(input_path, channels, output_path, spectroname, ffmpeg_path)


if __name__ == "__main__":
    main()
