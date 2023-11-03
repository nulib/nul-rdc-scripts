import dataparsing
import errortiers
import overallstatistics
import videoanalysis
from argparser import args

filepath = args.input_file

#Parses the raw XML into individual readings by frame (determined by frametime)
videodata = dataparsing.dataparsingandtabulatingvideo(filepath)
audiodata = dataparsing.dataparsingandtabulatingaudio(filepath)

#Collects the video summary data - outputs CSV and Dictionary
videostats = overallstatistics.videodatastatistics(videodata)

videofeedtodict = overallstatistics.videostatstodict(videostats)
videofeedtocsv = overallstatistics.videostatstocsv(videostats)

#Collects the audio summary data - outputs CSV and Dictionary
audiostats = overallstatistics.audiodatastatistics(audiodata)

audiofeedtodict = overallstatistics.audiostatstodict(audiostats)
audiofeedtocsv = overallstatistics.audiostatstocsv(audiostats)

#Video analysis for summary report
summaryvideoerrors = videoanalysis.checkAllVideo(videostats, args.videobitdepth)

#Assigns errors to tiers for verbose reporting
errortiers.errorsvideo(summaryvideoerrors)
