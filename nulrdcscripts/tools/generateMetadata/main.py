import os
import subprocess
import json
from nulrdcscripts.tools.generateMetadata.params import args

def audio (file,ffprobe_path):
    audio_output=json.loads(subprocess.check_output([ffprobe_path,"-v","error","-select_streams","a","-show_entries","stream=codec_long_name,bits_per_raw_sample, sample_rate, channels",file, "-of", "json"]).decode("ascii").rstrip())


def data (file,ffprobe_path):
    data_output=json.loads(subprocess.check_output([ffprobe_path,"-v","error","-select_streams","d","-show_entries","stream=codec_tag_string",file,"-of","json"]).decode("ascii").rstrip())
    return data_output


def attachment (file,ffprobe_path):
    attachment_output=json.loads(subprocess.check_output([ffprobe_path,"-v","error","-select_streams","t","-show_entries","stream_tags=filename",file,"-of","json"]).decode("ascii").rstrip())
    tags = [streams.get("tags") for streams in (attachment_output["streams"])]
    attachment_list=[]
    for i in tags:
        attachmentFilename = [i.get("filename")]
        attachment_list.extend(attachmentFilename)
    return attachment_output

def metadatalistsaudio(audio_output,data_output):
    audio_codec_name_list = [stream.get("codec_long_name")for stream in (audio_output["streams"])]
    audio_bit_rate = [stream.get("audio_bit_rate")for stream in (audio_output["streams"])]
    audio_sample_rate=[stream.get("audio_sample_rate")for stream in (audio_output["streams"])]
    audio_channels = [stream.get("channels")for stream in (audio_output["streams"])]

def metadatalistsvideo(video_output,audio_output,data_output):
    video_codec_name_list=[stream.get("codec_name") for stream in (video_output["streams"])]
    data_streams=[stream.get("codec_tag_string") for stream in (data_output["streams"])]
    width=[stream.get("width") for stream in (video_output["streams"])][0]
    height=[stream.get("height") for stream in (video_output["streams"])][0]
    pixel_format = [stream.get("pix_fmt") for stream in (video_output["streams"])][0]
    sar=[stream.get["sample_aspect_ratio"]for stream in (video_output["streams"])][0]
    dar=[stream.get["display_aspect_ratio"]for stream in (video_output["streams"])][0]
    frame_rate=[stream.get["avg_frame_rate"]for stream in (video_output["streams"])][0]
    color_space=[stream.get["color_space"]for stream in (video_output["streams"])][0]
    color_range=[stream.get["color_range"]for stream in (video_output["streams"])][0]
    color_transfer=[stream.get["color_transfer"]for stream in (video_output["streams"])][0]
    color_primaries = [stream.get["color_primaries"]for stream in (video_output["streams"])][0]
    tupAudio=metadatalistsaudio(audio_output,data_output)
def video(file,ffprobe_path):
    video_output = json.loads(subprocess.checkoutput([ffprobe_path, "-v","error","-select-streams","v","-show_entries", "stream=codec_name,avg_frame_rate,codec_time_base,width,height,pix_fmt,sample_aspect_ratio,display_aspect_ratio,color_range,color_space,color_transfers,color_primaries, chroma_location, field_order, codec_tag_string",file,"-of","json",]).decode("ascii").rstrip())
    audio_output=audio(file)
    data_output = data(file,ffprobe_path)
    attachment_output=attachment(file,ffprobe_path)
def ffprobe_report_solo(filename):
    ffprobe_path=os.path.abspath(args.ffprobe_path)
    