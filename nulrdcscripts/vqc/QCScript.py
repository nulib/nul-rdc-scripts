import os
import setup
from argparser import args
from nulrdcscripts.vqc import dataparsing
from nulrdcscripts.vqc import overallStatistics
from nulrdcscripts.vqc import framebyframestatistics
import progressbar

inputPath = os.path.normpath(args.input_path)
bitDepth = args.videobitdepth
outputPath = args.output_path

print("***Starting Setup***")
with progressbar.ProgressBar(max_value=100) as setupBar:
    for i in range(100):
        standardDF = setup.setVideoBitDepth(bitDepth)
        setupBar.update(i)
        setup.inputCheck(inputPath)
        setupBar.update(i)
        outputLocation = setup.outputCheck(inputPath, outputPath)
        setupBar.update(i)
        inputFileType = setup.setInputFileType(inputPath)
print("***Setup Complete***")

print("***Parsing File Video***")

if inputFileType == "JSON":
    with progressbar.ProgressBar(max_value=100) as parsingBar:
        for i in range(100):
            # audiodata = dataparsing.dataparsingandtabulatingaudioJSON(inputPath)
            parsingBar.update(i)
            videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
else:
    with progressbar.ProgressBar(max_value=100) as parsingBar:
        for i in range(100):
            # audiodata = dataparsing.dataparsingandtabulatingaudioXML(inputPath)
            parsingBar.update(i)
            videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
print("***Parsing complete***")

print("***Generating Full Video Descriptive Statistics***")
sumdatavideo = dataparsing.videodatastatistics(videodata)
# sumdataaudio = dataparsing.audiodatastatistics(audiodata)
sumdatavideocsv = dataparsing.videostatsdftocsv(sumdatavideo)
# sumdataaudiocsv = dataparsing.audiostatstocsv(sumdataaudio)
print("***Generated Full Video Descriptive Statistics***")

print("***Analysing Full Video Descriptive Statistics***")
overallStatistics.runOverallVideo(standardDF, sumdatavideo)
print("***Generated report for full video descriptive statistics***")

print("***Analyzing video for frame by frame statistics***")
frameerrors = framebyframestatistics.runfbyfanalysis(standardDF, videodata)
framebyframestatistics.dictodftojson(frameerrors)
print("***Analyzed frame by frame video statisitics***")
