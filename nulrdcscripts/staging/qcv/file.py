from parseandclean import dataparsing
from videoanalyses import videoanalysis, errortiers, overallstatistics


def runIndividualFile(inputpath, videoBitDepth):
    # Parses the raw XML into individual readings by frame (determined by frametime)
    videodata = dataparsing.dataparsingandtabulatingvideo(inputpath)
    audiodata = dataparsing.dataparsingandtabulatingaudio(inputpath)

    # Collects the video summary data - outputs CSV and Dictionary
    videostats = overallstatistics.videodatastatistics(videodata)

    videofeedtodict = overallstatistics.videostatstodict(videostats)
    videofeedtocsv = overallstatistics.videostatstocsv(videostats)

    # Collects the audio summary data - outputs CSV and Dictionary
    audiostats = overallstatistics.audiodatastatistics(audiodata)

    audiofeedtodict = overallstatistics.audiostatstodict(audiostats)
    audiofeedtocsv = overallstatistics.audiostatstocsv(audiostats)

    # Video analysis for summary report
    summaryvideoerrors = videoanalysis.checkAllVideo(videostats, videoBitDepth)

    # Assigns errors to tiers for verbose reporting
    errortiers.errorsvideo(summaryvideoerrors)
