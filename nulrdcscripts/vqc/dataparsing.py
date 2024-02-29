import pandas as pd
from nulrdcscripts.vqc import cleaners
import xml.etree.ElementTree as etree


def dataparsingandtabulatingaudioXML(inputPath):
    """Cleans and parses the audio data from XML for analysis. Returns dataframe."""
    audiodata = {}
    framenumberA = 0
    for event, elem in etree.iterparse(inputPath, events=["end"]):
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
    return dfAudio


def dataparsingandtabulatingvideoXML(inputPath):
    """Cleans and parses the video data from XML for analysis. Returns dataframe and generates csv."""
    videodata = {}
    framenumberV = 0

    for event, elem in etree.iterparse(inputPath, events=["end"]):
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
    return dfVideo


def videodatastatistics(videodata):
    """Generates descriptive video statistics for the entire video in a dataframe"""
    videostatsDSDF = videodata.describe()
    return videostatsDSDF


def audiodatastatistics(audiodata):
    """Generates descriptive audio statistics for the entire video in a dataframe"""
    audiodataDSDF = audiodata.describe()
    return audiodataDSDF


def videostatstocsv(videoDSDF):
    """Takes video descriptive statistics and puts them into a csv file"""
    summarydatavideocsv = videoDSDF.to_csv("videosummarystats.csv", index=True)
    return summarydatavideocsv


def audiostatstocsv(audioDSDF):
    """Takes audio descriptive statistics and puts them into a csv file."""
    summarydataaudiocsv = audioDSDF.to_csv("audiosummarystats.csv", index=True)
    return summarydataaudiocsv
