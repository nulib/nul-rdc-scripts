import pandas as pd
import xml.etree.ElementTree as etree
import json

videodata = {}
audiodata = {}


file = "example.xml"
data = "data.json"
for event, elem in etree.iterparse(file, events=("start",)):
    if elem.tag == "frame":
        frame = 1
        mediatype = elem.attrib["media_type"]
        if mediatype == "audio":
            for child in elem:
                criteria = child.attrib["key"]
                value = child.attrib["value"]
                frametime = elem.attrib["pkt_pts_time"]
            audiodata[frametime] = {}
            audiodata[frametime][criteria] = value
            elem.clear()
            dfAudio = pd.DataFrame.from_dict(audiodata)
            dfAudio = dfAudio.transpose()
            audiodata.clear()
        elif mediatype == "video":
            for child in elem:
                criteria = child.attrib["key"]
                value = child.attrib["value"]
                frametime = elem.attrib["pkt_pts_time"]
            videodata[frame] = {}
            videodata[frame]["Frame Time"] = float(frametime)
            videodata[frame][criteria] = float(value)
            elem.clear()
            frame = frame + 1

        dfVideo = pd.DataFrame.from_dict(videodata)
        dfVideo = dfVideo.transpose()
        videodata.clear()


df = dfAudio.to_csv("audiodata.csv", sep=",", header=True)
df = dfVideo.to_csv("video.csv", sep=",", header=True)
