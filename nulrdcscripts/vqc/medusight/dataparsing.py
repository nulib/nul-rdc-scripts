import pandas as pd
import cleaners
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


def dataparsingandtabulatingvideoXML(
    inputPath, parallel_threshold_mb=500, batch_size=10000
):
    """
    Chooses single-threaded or parallel parsing based on file size.
    parallel_threshold_mb: file size in MB above which to use parallel parsing.
    batch_size: number of frames per batch for parallel parsing.
    """
    file_size_mb = os.path.getsize(inputPath) / (1024 * 1024)
    print(f"Video XML file size: {file_size_mb:.1f} MB")
    if file_size_mb < parallel_threshold_mb:
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
    else:
        print("Using parallel batched parsing.")
        from concurrent.futures import ProcessPoolExecutor
        import progressbar

        rows = []
        frame_xmls = []
        max_workers = get_cpu_count()
        context = etree.iterparse(inputPath, events=("end",))
        total_frames = 0
        # First, scan the file to count frames (optional, for accurate progress)
        for event, elem in etree.iterparse(inputPath, events=("end",)):
            if (
                event == "end"
                and elem.tag == "frame"
                and elem.get("media_type") == "video"
            ):
                total_frames += 1
            elem.clear()

        # Now parse in batches with progress bar
        with progressbar.ProgressBar(max_value=total_frames) as bar:
            processed = 0
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                for event, elem in context:
                    if (
                        event == "end"
                        and elem.tag == "frame"
                        and elem.get("media_type") == "video"
                    ):
                        frame_xmls.append(etree.tostring(elem))
                        elem.clear()
                        if len(frame_xmls) >= batch_size:
                            batch_rows = list(executor.map(parse_frame_xml, frame_xmls))
                            rows.extend(batch_rows)
                            processed += len(frame_xmls)
                            print(f"Processed {processed} frames so far...")
                            bar.update(processed)
                            frame_xmls = []
                if frame_xmls:
                    batch_rows = list(executor.map(parse_frame_xml, frame_xmls))
                    rows.extend(batch_rows)
                    processed += len(frame_xmls)
                    print(f"Processed {processed} frames so far...")
                    bar.update(processed)
        dfVideo = pd.DataFrame(rows)
        return dfVideo


def videodatastatistics(videodata):
    """Generates descriptive video statistics for the entire video in a dataframe"""
    numeric = videodata.select_dtypes(include="number")
    videostatsDSDF = numeric.describe()
    return videostatsDSDF


def audiodatastatistics(audiodata):
    """Generates descriptive audio statistics for the entire video in a dataframe"""
    numeric = audiodata.select_dtypes(include="number")
    audiodataDSDF = numeric.describe()
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
