import pandas as pd
import parseandclean.cleaners as cleaners
from bs4 import BeautifulSoup


def dataparsingandtabulatingaudio(inputpath):
    """Cleans and parses the audio data for analysis. Returns dataframe."""
    audiodata = {}
    file = open(inputpath)
    contents = file.read()
    soup = BeautifulSoup(contents, "xml")
    contents = file.read()
    for frames in soup.find_all("frame"):
        taglist = frames.find_all("tag")
        frametime = frames.get("pkt_pts_time")
        mediatype = frames.get("media_type")
        if mediatype == "audio":
            audiodata[frametime] = {}
            for tag in taglist:
                tagkey = tag.get("key")
                if tagkey == "lavfi.astats.1.Noise_floor":
                    pass
                elif tagkey == "lavfi.astats.2.Noise_floor":
                    pass
                elif tagkey == "lavfi.astats.Overall.Noise_floor":
                    pass
                else:
                    cleankey = cleaners.tagkeycleaning(tagkey)
                    tagvalue = tag.get("value")
                    audiodata[frametime][cleankey] = float(tagvalue)
        else:
            pass
    audiodf = pd.DataFrame.from_dict(audiodata, orient="index")
    return audiodf


# filepath = "example.xml"
def dataparsingandtabulatingvideo(inputpath):
    """Cleans and parses the video data for analysis. Returns dataframe."""
    videodata = {}
    file = open(inputpath)
    contents = file.read()
    soup = BeautifulSoup(contents, "xml")
    contents = file.read()
    frame = 0
    for frames in soup.find_all("frame"):
        taglist = frames.find_all("tag")
        frametime = frames.get("pkt_pts_time")
        mediatype = frames.get("media_type")
        if mediatype == "video":
            frame = frame + 1
            videodata[frame] = {}
            for tag in taglist:
                tagkey = tag.get("key")
                cleankey = cleaners.tagkeycleaning(tagkey)
                tagvalue = tag.get("value")
                videodata[frame]["Frame Time"] = float(frametime)
                videodata[frame][cleankey] = float(tagvalue)
        else:
            pass
    videodf = pd.DataFrame.from_dict(videodata, orient="index")
    videodf = videodf.rename_axis("Frame")
    return videodf


# Dataframes returned contain information about every frame in the video. This will be used on its own and then will also be used to generate descriptive statistics for the entire video
