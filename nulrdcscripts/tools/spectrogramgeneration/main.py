# Coded with the help of Microsoft CoPilot

import os
import subprocess
import progressbar
from concurrent.futures import ThreadPoolExecutor
from nulrdcscripts.tools.spectrogramgeneration.params import args


def generate_spectrogram(input_path, channel, output_path, spectroname, ffmpegpath):
    """Creates a spectrogram for a single audio track in the input"""
    spectrogram_resolution = "1920x1080"  # Updated resolution
    output = os.path.join(output_path, f"{spectroname}_spectrogram0{channel + 1}_s.png")
    spectrogram_args = [ffmpegpath]
    spectrogram_args += ["-loglevel", "error", "-y"]
    spectrogram_args += ["-i", input_path, "-lavfi"]
    if channel > 1:
        spectrogram_args += [
            f"[0:a:{channel}]showspectrumpic=mode=separate:s={spectrogram_resolution}"
        ]
    else:
        spectrogram_args += [
            f"[0:a:{channel}]showspectrumpic=s={spectrogram_resolution}"
        ]
    spectrogram_args += [output]
    subprocess.run(spectrogram_args)
    print(f"*** Spectrogram for channel {channel + 1} generated ***")


def generate_all_spectrograms(
    input_path, channels, output_path, spectroname, ffmpegpath
):
    """Creates spectrograms for all audio channels in parallel"""
    widgets = [
        " [",
        progressbar.Percentage(),
        "] ",
        progressbar.Bar(),
        " (",
        progressbar.ETA(),
        ") ",
    ]
    bar = progressbar.ProgressBar(max_value=int(channels), widgets=widgets)
    bar.start()

    with ThreadPoolExecutor(max_workers=int(channels)) as executor:
        futures = [
            executor.submit(
                generate_spectrogram,
                input_path,
                index,
                output_path,
                spectroname,
                ffmpegpath,
            )
            for index in range(int(channels))
        ]
        for i, future in enumerate(futures):
            future.result()
            bar.update(i + 1)

    bar.finish()


def softwarecheck(software, softwarename):
    """Checks that software exists"""
    version = "--version" if "sox" in software else "-version"
    try:
        subprocess.check_output([software, version]).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        raise Exception(f"Cannot locate {softwarename}. Check path.")


def getnumberchannels(ffprobe_path, input_path):
    command = [
        ffprobe_path,
        "-i",
        input_path,
        "-show_entries",
        "stream=channels",
        "-select_streams",
        "a:0",
        "-of",
        "compact=p=0:nk=1",
        "-v",
        "0",
    ]
    output = subprocess.run(command, capture_output=True, text=True)
    channels = output.stdout.strip()
    return channels


def checkOrCreateOutput(output_path, input_path):
    if output_path == "NA":
        output_path = input_path
    if not os.path.isdir(output_path):
        output_path = os.path.dirname(output_path)
    return output_path


def callableSpectrogram(ffprobe_path, input_path, output_path, ffmpeg_path):
    channels = getnumberchannels(ffprobe_path, input_path)
    spectroname, _ = os.path.splitext(os.path.basename(input_path))
    generate_all_spectrograms(
        input_path, channels, output_path, spectroname, ffmpeg_path
    )


def main():
    """Only runs if you are running this command on its own"""
    input_path = args.input_path
    ffprobe_path = args.ffprobe_path
    ffmpeg_path = args.ffmpeg_path
    sox_path = args.sox_path
    softwarecheck(sox_path, "sox")
    softwarecheck(ffprobe_path, "ffprobe")
    softwarecheck(ffmpeg_path, "ffmpeg")
    output_path = args.output_path
    output_path = checkOrCreateOutput(output_path, input_path)
    callableSpectrogram(ffprobe_path, input_path, output_path, ffmpeg_path)


if __name__ == "__main__":
    main()
