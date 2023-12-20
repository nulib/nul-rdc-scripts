import pandas as pd
import parseandclean.cleaners as cleaners
import xml.etree.ElementTree as etree


def dataparsingandtabulatingaudio(inputpath):
    """Cleans and parses the audio data for analysis. Returns dataframe and generates csv."""
    audiodata = {}
    framenumberA = 0
    for event, elem in etree.iterparse(inputpath, events=["end"]):
        if event == "end":
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
                elem.clear()
    dfAudio = pd.DataFrame.from_dict(audiodata)
    dfAudio = dfAudio.transpose()
    dfAudio.to_csv("audiodata.csv", sep=",")
    return dfAudio


# filepath = "example.xml"
def dataparsingandtabulatingvideo(inputpath):
    """Cleans and parses the video data for analysis. Returns dataframe and generates csv."""
    videodata = {}
    framenumberV = 0

    for event, elem in etree.iterparse(inputpath, events=["end"]):
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
    dfVideo = pd.DataFrame.from_dict(videodata)
    dfVideo = dfVideo.transpose()
    dfVideo.to_csv("videodatashort.csv", sep=",")
    return dfVideo
