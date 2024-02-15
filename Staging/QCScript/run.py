import dataparsing
import videoanalysis
import overallstatistics
import csvgeneration

filepath = input("Filepath")


videodata = dataparsing.dataparsingandtabulatingvideo(filepath)
audiodata = dataparsing.dataparsingandtabulatingaudio(filepath)

videostats = overallstatistics.videodatastatistics(videodata)
audiostats = overallstatistics.audiodatastatistics(audiodata)


"""
videoanalysis.videoanalyzer(videodata)
"""
