import os
import subprocess
from nulrdcscripts.tools.ffplaywindow.scriptparser import args


def declareFfplayfilter(font):
    return (
        "-vf split=5[a][b][c][d][e];[a]copy,drawtext=text='%{pts\\:hms}':box=1:boxborderw=5:x=(w-text_w)/2:y=h-(text_h*2):fontsize=20:fontfile="
        + font
        + "[a1];[b]field=top,format=yuv422p,waveform=scale=digital:intensity=0.1:mode=column:mirror=1:c=1:f=lowpass:e=instant:graticule=green:flags=numbers+dots[b1];[c]field=bottom,format=yuv422p,waveform=scale=digital:intensity=0.1:mode=column:mirror=1:c=1:f=lowpass:e=instant:graticule=green:flags=numbers+dots[c1];[d]format=yuv422p,vectorscope=i=0.04:mode=color2:c=1:envelope=instant:graticule=green:flags=name,scale=512:512,drawbox=w=9:h=9:t=1:x=128-3:y=512-452-5:c=sienna@0.8,drawbox=w=9:h=9:t=1:x=160-3:y=512-404-5:c=sienna@0.8,drawbox=w=9:h=9:t=1:x=192-3:y=512-354-5:c=sienna@0.8,drawbox=w=9:h=9:t=1:x=224-3:y=512-304-5:c=sienna@0.8,drawgrid=w=32:h=32:t=1:c=white@0.1,drawgrid=w=256:h=256:t=1:c=white@0.2[d1];[e]scale=512:ih,signalstats='out=brng:color="
        + args.highlight_color
        + "'"
        + "[e1];[a1][b1][c1][e1][d1]xstack=inputs=5:layout='0_0|0_h0|0_h0+h1|w0_0|w0_h0' -af channelmap='0|1:stereo'"
    )


def main():
    input_path = os.path.normpath(args.input_path)
    ffplay_path = os.path.normpath(args.ffplay_path)
    ostype = os.name

    if ostype == "nt":
        font = "/Windows/Fonts/arial.ttf"
        ffplayfilter = declareFfplayfilter(font)
        command = ffplay_path + " " + "-i" + " " + input_path + " " + ffplayfilter
    else:
        font = "/Library/Fonts/Arial.ttf"  # Specify a valid font path for macOS
        ffplayfilter = declareFfplayfilter(font)
        command = [
            'ffplay', input_path,
            '-vf', (
                'split=5[a][b][c][d][e];'
                '[a]copy,drawtext=text=\'%{pts\\:hms}\':box=1:boxborderw=5:x=(w-text_w)/2:y=h-(text_h*2):fontsize=20:fontfile=font[a1];'
                '[b]field=top,format=yuv422p,waveform=scale=digital:intensity=0.1:mode=column:mirror=1:c=1:f=lowpass:e=instant:graticule=green:flags=numbers+dots[b1];'
                '[c]field=bottom,format=yuv422p,waveform=scale=digital:intensity=0.1:mode=column:mirror=1:c=1:f=lowpass:e=instant:graticule=green:flags=numbers+dots[c1];'
                '[d]format=yuv422p,vectorscope=i=0.04:mode=color2:c=1:envelope=instant:graticule=green:flags=name,scale=512:512,'
                'drawbox=w=9:h=9:t=1:x=128-3:y=512-452-5:c=sienna@0.8,drawbox=w=9:h=9:t=1:x=160-3:y=512-404-5:c=sienna@0.8,'
                'drawbox=w=9:h=9:t=1:x=192-3:y=512-354-5:c=sienna@0.8,drawbox=w=9:h=9:t=1:x=224-3:y=512-304-5:c=sienna@0.8,'
                'drawgrid=w=32:h=32:t=1:c=white@0.1,drawgrid=w=256:h=256:t=1:c=white@0.2[d1];'
                '[e]scale=512:ih,signalstats=out=brng:color=red[e1];'
                '[a1][b1][c1][e1][d1]xstack=inputs=5:layout=0_0|0_h0|0_h0+h1|w0_0|w0_h0'
            ),
            '-af', 'channelmap=0|1:stereo'
]

# Run the ffplay command
    subprocess.run(command)

    print(
        "To exit the playback window, while in window use the 'esc' key. To fast-forward or rewind, use the respective arrow keys."
    )


if __name__ == "__main__":
    main()
