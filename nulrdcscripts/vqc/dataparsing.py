import pandas as pd
from nulrdcscripts.vqc import cleaners
from lxml import etree  # switched to lxml for faster XML parsing


def dataparsingandtabulatingaudioXML(inputPath):
    """Cleans and parses the audio data from XML for analysis. Returns dataframe."""
    rows = []
    for event, elem in etree.iterparse(inputPath, events=("end",)):
        if event == "end" and elem.tag == "frame" and elem.get("media_type") == "audio":
            row = {}
            frametime = elem.get("pkt_pts_time")
            row["Frame Time"] = float(frametime)
            for tag in elem.iter("tag"):
                criteria = tag.attrib["key"]
                criteria = cleaners.criteriacleaner(criteria)
                value = tag.attrib["value"]
                try:
                    row[criteria] = float(value)
                except ValueError:
                    row[criteria] = value
            rows.append(row)
            elem.clear()
    dfAudio = pd.DataFrame(rows)
    return dfAudio


def dataparsingandtabulatingvideoXML(inputPath):
    """Cleans and parses the video data from XML for analysis. Returns dataframe and generates csv."""
    rows = []
    for event, elem in etree.iterparse(inputPath, events=("end",)):
        if event == "end" and elem.tag == "frame" and elem.get("media_type") == "video":
            row = {}
            frametime = elem.get("pkt_pts_time")
            row["Frame Time"] = float(frametime)
            for tag in elem.iter("tag"):
                criteria = tag.attrib["key"]
                criteria = cleaners.criteriacleaner(criteria)
                value = tag.attrib["value"]
                try:
                    row[criteria] = float(value)
                except ValueError:
                    row[criteria] = value
            rows.append(row)
            elem.clear()
    dfVideo = pd.DataFrame(rows)
    return dfVideo


def videodatastatistics(videodata):
    """Generates descriptive video statistics for the entire video in a dataframe"""
    videostatsDSDF = videodata.describe()
    return videostatsDSDF


def audiodatastatistics(audiodata):
    """Generates descriptive audio statistics for the entire video in a dataframe"""
    audiodataDSDF = audiodata.describe()
    return audiodataDSDF


def videostatstocsv(videoDSDF, outputpath):
    """Takes video descriptive statistics and puts them into a csv file"""
    outputpath = outputpath + "/videosummarystats.csv"
    summarydatavideocsv = videoDSDF.to_csv(outputpath, index=True)
    return summarydatavideocsv


def audiostatstocsv(audioDSDF, outputpath):
    """Takes audio descriptive statistics and puts them into a csv file."""
    outputpath = outputpath + "/audiosummarystats.csv"
    summarydataaudiocsv = audioDSDF.to_csv(outputpath, index=True)
    return summarydataaudiocsv
