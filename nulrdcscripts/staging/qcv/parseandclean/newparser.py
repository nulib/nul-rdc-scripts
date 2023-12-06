import pandas as pd
import xml.etree.ElementTree as etree
import json

videodata = {}

file = "example.xml"
data = "data.json"
with open(data, "w", newline="") as jsonfile:
    for event, elem in etree.iterparse(file, events=("start",)):
        if elem.tag == "frame":
            frametime = elem.attrib["pkt_pts_time"]
        elif elem.tag == "tag":
            for tag in elem.tag:
                criteria = elem.attrib["key"]
                value = elem.attrib["value"]
                videodata["Frametime"] = float(frametime)
                videodata[criteria] = value
        json.dump(videodata, jsonfile)
        videodata.clear()
        elem.clear()
