import dataparsing

inputpath = "Z:\\RDC\\SCRATCH\\sophiatestfiles\\test_badLevels\\test\\badlevels2\\a\\badlevels2_a_framebyframe.xml"


def runIndividualFile(inputpath):
    # Parses the raw XML into individual readings by frame (determined by frametime)
    videodata = dataparsing.dataparsingandtabulatingvideoXML(inputpath)
    audiodata = dataparsing.dataparsingandtabulatingaudioXML(inputpath)

    # Collects the video summary data - outputs CSV and Dictionary
    videostats = dataparsing.videodatastatistics(videodata)

    # videofeedtodict = dataparsing.videostatstodict(videostats)
    videofeedtocsv = dataparsing.videostatstocsv(videostats)

    # Collects the audio summary data - outputs CSV and Dictionary
    # audiostats = overallstatistics.audiodatastatistics(audiodata)

    # audiofeedtodict = overallstatistics.audiostatstodict(audiostats)
    # audiofeedtocsv = overallstatistics.audiostatstocsv(audiostats)

    # Video analysis for summary report
    # summaryvideoerrors = videoanalysis.checkAllVideo(videostats, videoBitDepth)

    # Assigns errors to tiers for verbose reporting
    # errortiers.errorsvideo(summaryvideoerrors)


runIndividualFile(inputpath)
