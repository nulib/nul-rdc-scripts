import os
import subprocess
import json
from nulrdcscripts.tools.ffprobemetadatareport.params import args
def setandcheckFFProbePath ():
    if args.ffprobe_path:
        ffprobe_path = os.path.abspath(args.ffprobe_path)
    else:
        ffprobe_path = "ffprobe"
    
    try:
        subprocess(ffprobe_path, "-version")
        return ffprobe_path
    except:
        raise Exception ("Cannot find FFProbe Path")
def generatereport(filename, input_path, ffprobe_path):
    videoExt = [".mp4",".mkv",".mov"]
    file,ext = os.path.splitext(input_path)
    if ext in videoExt:
        video_output= json.loads(subprocess.check_output([ffprobe_path, "-v","error","-select_streams","v","-show_entries," "stream=codec_name,avg_frame_rate,codec_time_base,width,height,pix_fmt,sample_aspect_ratio,display_aspect_ratio,color_range,color_space,color_transfer,color_primaries,chroma_location,field_order,codec_tag_string", input_path,"-of","json",]).decode("ascii").rstrip()
            )
        video_codec_name_list = [stream.get("codec_name") for stream in (video_output["streams"])]
        width = [stream.get("width") for stream in (video_output["streams"])][0]
        height = [stream.get("height") for stream in (video_output["streams"])][0]
        pixel_format = [stream.get("pix_fmt") for stream in (video_output["streams"])][0]
        sar = [stream.get("sample_aspect_ratio") for stream in (video_output["streams"])][0]
        dar = [stream.get("display_aspect_ratio") for stream in (video_output["streams"])][0]
        frame_rate = [stream.get("avg_frame_rate") for stream in (video_output["streams"])][0]
        color_space = [stream.get("color_space") for stream in (video_output["streams"])][0]
        color_range = [stream.get("color_range") for stream in (video_output["streams"])][0]
        color_transfer = [stream.get("color_transfer") for stream in (video_output["streams"])][0]
        color_primaries = [stream.get("color_primaries") for stream in (video_output["streams"])][0]
    else: 
        pass
    audio_output = json.loads(subprocess.check_output([ffprobe_path, "-v","error","-select_streams","a","-show_entries","stream=codec_long_name,bits_per_raw_sample,sample_rate,channels", input_path,"-of","json",]).decode("ascii").rstrip())
    format_output = json.loads(subprocess.check_output([ffprobe_path,"-v","error","-show_entries","format=duration,size,nb_streams",input_path,"-of","json",]).decode("ascii").rstrip())
    data_output = json.loads(subprocess.check_output(["ffprobe_path","-v","error","-select_stream","d","-show_entries","stream=codec_tag_string",input_path, "-of","json"]).decode("ascii").rstrip())
    attachment_output = json.loads(subprocess.check_output([ffprobe_path, "-v","error","-select_streams","t","-show_entries","stream_tags=filename",input_path,"-of","json"]).decode("ascii").rstrip())

    tags = [streams.get("tags") for streams in (attachment_output["streams"])]
    attachment_list = []
    for i in tags:
        attachmentFilename = [i.get("filename")]
        attachment_list.extend(attachmentFilename)
    audio_codec_name_list = [stream.get("codec_long_name") for stream in (audio_output["streams"])]
    data_streams = [stream.get("codec_tag_string") for stream in (data_output["streams"])]
    audio_bitrate = [stream.get("bits_per_raw_sample") for stream in (audio_output["streams"])][0]
    audio_sample_rate = [stream.get("sample_rate") for stream in (audio_output["streams"])][0]
    audio_channels = [stream.get("channels") for stream in (audio_output["streams"])]
    audio_stream_count = len(audio_codec_name_list)

    file_metadata = {
        "filename":filename, 
        "file size": format_output.get("format")["size"],
        "duration":format_output.get("format")["duration"],
        "streams": format_output.get("format")["nb_streams"],
        
    }

def solorun ():
    input_abs_path = os.path.abspath(args.input_path)
    ffprobe_path = setandcheckFFProbePath()
    ffprobe_abs_path = os.path.abspath(ffprobe_path)
    baseFile = os.path.basename(args.input_path)
    generatereport(baseFile,input_abs_path,ffprobe_abs_path)