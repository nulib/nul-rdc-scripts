import dataparsing
import videoanalysis
import overallstatistics
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues

filepath = input("Filepath")

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


summaryvideoerrors = videoanalysis.checkAllVideo(videostats, tenBitVideoValues)





