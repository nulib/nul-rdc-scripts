import pandas as pd
import keycleaner as keycleaner
import overallstatistics as overallstatistics
from bs4 import BeautifulSoup
from tabulate import tabulate


def dataparsingandtabulatingaudio(filepath):
    audiodata = {}
    file = open(filepath)
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
                    cleankey = keycleaner.tagkeycleaning(tagkey)
                    tagvalue = tag.get("value")
                    audiodata[frametime][cleankey] = float(tagvalue)
        else:
            pass
    audiodf = pd.DataFrame.from_dict(audiodata, orient="index")
    return audiodf


def dataparsingandtabulatingvideo(filepath):
    videodata = {}
    file = open(filepath)
    contents = file.read()
    soup = BeautifulSoup(contents, "xml")
    contents = file.read()
    for frames in soup.find_all("frame"):
        taglist = frames.find_all("tag")
        frametime = frames.get("pkt_pts_time")
        mediatype = frames.get("media_type")
        if mediatype == "video":
            videodata[frametime] = {}
            for tag in taglist:
                tagkey = tag.get("key")
                cleankey = keycleaner.tagkeycleaning(tagkey)
                tagvalue = tag.get("value")
                videodata[frametime][cleankey] = float(tagvalue)
        else:
            pass
    videodf = pd.DataFrame.from_dict(videodata, orient="index")
    return videodf


# Dataframes returned contain information about every frame in the video. This will be used on its own and then will also be used to generate descriptive statistics for the entire video