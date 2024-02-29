import os
import setup
from argparser import args
from nulrdcscripts.vqc import overallStatistics
from nulrdcscripts.vqc import dataparsing
from progress.bar import ChargingBar

inputPath = os.path.normpath(args.input_path)
outputPath = os.path.normpath(args.output_path)
bitDepth = args.videobitdepth


print("*****Starting Setup*****")
setupBar = ChargingBar("Setting Up", max=20)
for i in range(20):
    standardDF = setup.setVideoBitDepth(bitDepth)
    setupBar.next()
    setup.inputCheck(inputPath)
    setupBar.next()
    outputLocation = setup.outputCheck(inputPath, outputPath)
    setupBar.next()
    inputFileType = setup.setInputFileType(inputPath)
    setupBar.finish()
print("*****Setup Complete*****")

print("*****Parsing File Video*****")
parsingBar = ChargingBar("Parsing file", max=20)

if inputFileType == "JSON":
    for i in range(20):
        audiodata = dataparsing.dataparsingandtabulatingaudioJSON(inputPath)
        parsingBar.next()
        videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
        parsingBar.finish()
else:
    for i in range(20):
        audiodata = dataparsing.dataparsingandtabulatingaudioXML(inputPath)
        parsingBar.next()
        videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
        parsingBar.finish()
print("*****Parsing complete*****")

print("*****Generating Full Video Descriptive Statistics*****")
videoDSDF = dataparsing.videodatastatistics(videodata)
audioDSDF = dataparsing.audiodatastatistics(audiodata)
sumVideoStatsCSV = dataparsing.videostatstocsv(videoDSDF)
sumAudioStatsCSV = dataparsing.audiostatstocsv(audioDSDF)
print("*****Generated Full Video Descriptive Statistics*****")

print("*****Analysing Full Video Descriptive Statistics*****")
