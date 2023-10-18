import DataParsing
import passfail
import overallstatistics
import csvgeneration

filepath = input("Filepath")


videodata = DataParsing.dataparsingandtabulatingvideo(filepath)
audiodata = DataParsing.dataparsingandtabulatingaudio(filepath)

videostats = overallstatistics.videodatastatistics(videodata)
audiostats = overallstatistics.audiodatastatistics(audiodata)
print(videostats)


