import os
import subprocess
from VideoScript.Arguments.Arguments import args


def generate_spectrogram(input, channel_layout_list, outputFolder, outputName):
    spectrogram_resolution = "1920x1080"
    for index, item in enumerate(channel_layout_list):
        output = os.path.join(outputFolder, outputName + "_0a" + str(index) + ".png")
        spectrogram_args = [args.ffmpeg_path]
        spectrogram_args += ["-loglevel", "error", "-y"]
        spectrogram_args += ["-i", input, "-lavfi"]
        if item > 1:
            spectrogram_args = +[
                "[0:a:%(a)s]showspectrumpic=s=%(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        else:
            spectrogram_args += [
                "[0:a:%(a)s]showspectrumpic=s=(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        spectrogram_args += [output]
        subprocess.run(spectrogram_args)
