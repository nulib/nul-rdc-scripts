import pandas as pd
import xml.etree.ElementTree as etree
import cleaners

audiodata = {}
videodata = {}
framenumberA = 0
framenumberV = 0


file = input("file")
data = "data.json"
tree = etree.parse(file)
root = tree.getroot()
"""
for event, elem in etree.iterparse(file, events=["start", "end"]):
    if event == "start":
        if elem.tag == "frame":
            if elem.get("media_type") == "audio":
                framenumberA = framenumberA + 1
                frametime = elem.get("pkt_pts_time")
                audiodata[framenumberA] = {}
                for tag in elem.iter("tag"):
                    criteria = tag.attrib["key"]
                    criteria = cleaners.criteriacleaner(criteria)
                    value = tag.attrib["value"]
                    audiodata[framenumberA]["Frame Time"] = float(frametime)
                    audiodata[framenumberA][criteria] = value
            else:
                pass
        else:
            pass
    elif event == "end":
        elem.clear()
"""

for event, elem in etree.iterparse(file, events=["end"]):
    if event == "end":
        if elem.tag == "frame":
            if elem.get("media_type") == "video":
                framenumberV = framenumberV + 1
                frametime = elem.get("pkt_pts_time")
                videodata[framenumberV] = {}
                for tag in elem.iter("tag"):
                    criteria = tag.attrib["key"]
                    criteria = cleaners.criteriacleaner(criteria)
                    value = tag.attrib["value"]
                    videodata[framenumberV]["Frame Time"] = float(frametime)
                    videodata[framenumberV][criteria] = float(value)
            elem.clear()
"""'
dfAudio = pd.DataFrame.from_dict(audiodata)
dfAudio = dfAudio.transpose()
dfAudio.to_csv("audiodata.csv", sep=",")
"""

dfVideo = pd.DataFrame.from_dict(videodata)
dfVideo = dfVideo.transpose()
dfVideo.to_csv("videodatashort.csv", sep=",")
