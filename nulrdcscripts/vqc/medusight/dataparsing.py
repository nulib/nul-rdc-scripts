import pandas as pd
from medusight import cleaners
from lxml import etree  # switched to lxml for faster XML parsing
from concurrent.futures import ProcessPoolExecutor
import os


def get_cpu_count():
    """Returns the number of available CPU cores."""
    count = os.cpu_count()
    print(f"Detected CPU cores: {count}")
    return count


def parse_frame_xml(frame_xml):
    """Parse a single <frame> element XML string into a dict."""
    elem = etree.fromstring(frame_xml)
    row = {}
    frametime=elem.get('pkts_pts_time')
    try:
        float(frametime)
    except:
        frametime = elem.get('pts_time')

    row["Frame Time"] = float(frametime)
    for tag in elem.iter("tag"):
        criteria = tag.attrib["key"]
        criteria = cleaners.criteriacleaner(criteria)
        value = tag.attrib["value"]
        try:
            row[criteria] = float(value)
        except ValueError:
            row[criteria] = value
    return row


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
    """
    Cleans and parses the video data from XML for analysis. Returns dataframe.
    Parallel processing removed; always uses single-threaded parsing.
    """
    file_size_mb = os.path.getsize(inputPath) / (1024 * 1024)
    print(f"Video XML file size: {file_size_mb:.1f} MB")
    print("Using single-threaded parsing.")
    rows = []
    for event, elem in etree.iterparse(inputPath, events=("end",)):
        if (
            event == "end"
            and elem.tag == "frame"
            and elem.get("media_type") == "video"
        ):
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
    numeric = videodata.select_dtypes(include="number").fillna(0)  # or .dropna()
    videostatsDSDF = numeric.describe()
    return videostatsDSDF


def audiodatastatistics(audiodata):
    """Generates descriptive audio statistics for the entire video in a dataframe"""
    numeric = audiodata.select_dtypes(include="number")
    audiodataDSDF = numeric.describe()
    return audiodataDSDF


def videostatstocsv(videoDSDF, outputpath,basefilename):
    """Takes video descriptive statistics and puts them into a csv file"""
    outputpath = outputpath + "/" + basefilename + "_videosummarystats.csv"
    summarydatavideocsv = videoDSDF.to_csv(outputpath, index=True)
    return summarydatavideocsv


def audiostatstocsv(audioDSDF, outputpath,basefilename):
    """Takes audio descriptive statistics and puts them into a csv file."""
    outputpath = outputpath + "/" + basefilename + "_audiosummarystats.csv"
    summarydataaudiocsv = audioDSDF.to_csv(outputpath, index=True)
    return summarydataaudiocsv
