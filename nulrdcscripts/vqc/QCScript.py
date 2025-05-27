import os
import progressbar
from argparser import args
from nulrdcscripts.vqc import dataparsing
import qcsetup as setup


def main():
    inputPath = os.path.normpath(args.input_path)
    bitDepth = args.videobitdepth
    outputPath = args.output_path

    print("*****Starting Setup*****")
    with progressbar.ProgressBar(max_value=4) as setupBar:
        setupBar.update(0)
        standardDF = setup.setVideoBitDepth(bitDepth)
        setupBar.update(1)
        setup.inputCheck(inputPath)
        setupBar.update(2)
        outputLocation = setup.outputCheck(inputPath, outputPath)
        setupBar.update(3)
        inputFileType = setup.setInputFileType(inputPath)
        setupBar.update(4)
    print("*****Setup Complete*****")

    print("*****Parsing File Video*****")
    parsingBar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    if inputFileType == "JSON":
        with progressbar.ProgressBar(max_value=100) as parsingBar:
            for i in range(100):
                audiodata = dataparsing.dataparsingandtabulatingaudioJSON(inputPath)
                parsingBar.update(i)
                videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
    else:
        with progressbar.ProgressBar(max_value=100) as parsingBar:
            for i in range(100):
                audiodata = dataparsing.dataparsingandtabulatingaudioXML(inputPath)
                parsingBar.update(i)
                videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
    print("*****Parsing complete*****")

    print("*****Generating Full Video Descriptive Statistics*****")
    videoDSDF = dataparsing.videodatastatistics(videodata)
    audioDSDF = dataparsing.audiodatastatistics(audiodata)

    # Determine output directory
    if outputPath == "input":
        outputDir = os.path.dirname(inputPath)
    else:
        outputDir = outputPath

    sumVideoStatsCSV = dataparsing.videostatstocsv(videoDSDF, outputDir)
    sumAudioStatsCSV = dataparsing.audiostatstocsv(audioDSDF, outputDir)
    print("*****Generated Full Video Descriptive Statistics*****")

    # print("*****Analysing Full Video Descriptive Statistics*****")


if __name__ == "__main__":
    main()
