import os
import subprocess
import progressbar
from nulrdcscripts.tools.AudioNormalizer.params import args



def normalizerAudio (input_file,norm_file):
    ffmpeg_normalize_path = args.ffmpeg_norm_path
    command = ffmpeg_normalize_path, input_file, "-o", norm_file, "-t -18", "--keep-loudness-range-target", "-tp", "-1", "-c:a pcm_s16l2 -ar 44100"
    subprocess.run(command)

def normalizerVideo (input_file,norm_file):
    ffmpeg_normalize_path = args.ffmpeg_norm_path
    command = ffmpeg_normalize_path + ' ' + input_file + ' '+ "-o"+ ' '+ norm_file+ ' '+"-t -18 --keep-loudness-range-target -tp -1 -c:a aac -b:a 256k -ar 48000"
    subprocess.run(command)

    
def single(input_path):
    filename, ext = os.path.splitext(input_path)
    output_path = filename + "_normalized" + ext
    if ext == ".wav":
        normalizerAudio(input_path,output_path)
    elif ext == ".mp4":
        normalizerVideo(input_path,output_path)

def batch(input_path):
    ext = ["_a.wav","_a.mp4"]
    for file in os.listdir(input_path):
        if file.endswith(".mp4.md5"):
            pass
        elif file.endswith(ext):
            single(file)

def run():
    input_path = os.path.normpath(args.input_path)
    fileType = os.path.isdir(input_path)
    if fileType:
        batch(input_path)
    else:
        single(input_path)

def main():
        run()

main()



