import os
import subprocess
from nulrdcscripts.tools.spectrogramgeneration.params import args

def generate_spectrogram(input_path,channels,outdir,spectroname,ffmpegpath):
    ''' Creates a spectrogram for each audio track in the input'''
    for index, item in enumerate(channels):
        spectrogram_resolution="1920x1080"
        output = os.path.join(outdir, spectroname + "_spectrogram0" + str(index+1)+"_s.png")
        spectrogram_args=[ffmpegpath]
        spectrogram_args += ["-loglevel","error","-y"]
        spectrogram_args += ["-i",input_path,"-lavfi"]
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

def ffprobecheck():
    '''Checks that ffprobe exists'''

    if args.ffprobe_path:
        ffprobe_path = os.path.abspath(args.ffprobe_path)
    else:
       ffprobe_path = "ffprobe"
    try:
        subprocess(ffprobe_path, "--version")
        return ffprobe_path
    except:
        raise Exception ("FFProbe path cannot be found")
    

def getnumberchannels(ffprobe_path,input_path):
    command = ffprobe_path +" "+ "-i" + " " + input_path + " " + "-show_entries stream=channels -select_streams a:0 -of compact=p=0:nk=1 -v 0"
    output = subprocess.run(command, capture_output=True, text=True)
    channels = output.stdout
    return channels

def main():
    '''Only runs if you are running this command on it's own'''
    input_path = os.path.abspath(args.input_path)
    ffprobe_path = ffprobecheck()
    channels = getnumberchannels(ffprobe_path)
    outdir = os.path.abspath(args.output_path)
    spectroname,ext = (os.path.basename(input)).splitext
    ffmpegpath = ffmpegcheck()
    generate_spectrogram(input_path,channels,outdir,spectroname,ffmpegpath)

    main()