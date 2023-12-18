import xml.etree.ElementTree as etree
import pandas as pd

tree = etree.parse("example.xml")
root = tree.getroot()
audiodata = {}
videodata = {}
framenumberA = 0
framenumberV = 0
for frame in root.findall("./frames/frame"):
    mediatype = frame.get("media_type")
    if mediatype == "audio":
        framenumberA = framenumberA + 1
        frametime = frame.get("pkt_pts_time")
        audiodata[framenumberA] = {}
        for tag in frame.iter("tag"):
            criteria = tag.attrib["key"]
            value = tag.attrib["value"]
            audiodata[framenumberA]["Frame Time"] = float(frametime)
            audiodata[framenumberA][criteria] = value
    elif mediatype == "video":
        framenumberV = framenumberV + 1
        frametime = frame.get("pkt_pts_time")
        videodata[framenumberV] = {}
        for tag in frame.iter("tag"):
            criteria = tag.attrib["key"]
            value = tag.attrib["value"]
            videodata[framenumberV]["Frame Time"] = float(frametime)
            videodata[framenumberV][criteria] = float(value)

dfAudio = pd.DataFrame.from_dict(audiodata)
dfAudio = dfAudio.transpose()
dfAudio.to_csv("audiodata.csv", sep=",")

dfVideo = pd.DataFrame.from_dict(videodata)
dfVideo = dfVideo.transpose()
dfVideo.to_csv("videodata.csv", sep=",")
