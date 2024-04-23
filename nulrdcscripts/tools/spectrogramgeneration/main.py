import os
import subprocess
from nulrdcscripts.tools.spectrogramgeneration.params import args

def generate_spectrogram(input,channel_layout_list,outdir,spectroname,ffmpegpath):
    ''' Creates a spectrogram for each audio track in the input'''
    for index, item in enumerate(channel_layout_list):
        spectrogram_resolution="1920x1080"
        output = os.path.join(outdir, spectroname + "_spectrogram0" + str(index+1)+"_s.png")
        spectrogram_args=[ffmpegpath]
        spectrogram_args += ["-loglevel","error","-y"]
        spectrogram_args += ["-i",input,"-lavfi"]
        if item > 1:
            spectrogram_args += ["[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s" % {"a":index,"b":spectrogram_resolution}]
        else:
            spectrogram_args += ["[0:a:%(a)s]showspectrumpic=s=%(b)s"%{"a":index,"b":spectrogram_resolution}]
        spectrogram_args += [output]
        subprocess.run(spectrogram_args)

def ffmpegcheck():
    '''Checks that ffmpeg exists'''

    if args.ffmpeg_path:
        ffmpegpath = os.path.abspath(args.ffmpeg_path)
    else:
       ffmpegpath = "ffmpeg"
    try:
        subprocess(ffmpegpath, "--version")
        return ffmpegpath
    except:
        raise Exception ("FFMPEG path cannot be found")
    

def main():
    '''Only runs if you are running this command on it's own'''
    input = os.path.abspath(args.input_path)
    channel_layout_list = "" #input path to ffprobe report to get input_metadata["techMetaA"]["channels"]
    outdir = os.path.abspath(args.output_path)
    spectroname,ext = (os.path.basename(input)).splitext
    ffmpegpath = ffmpegcheck()
    generate_spectrogram(input,channel_layout_list,outdir,spectroname,ffmpegpath)