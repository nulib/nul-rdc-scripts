import os
import progressbar
from nulrdcscripts.vqc.params import args
from nulrdcscripts.vqc import dataparsing
import qcsetup


def main():
    inputPath = os.path.normpath(args.input_path)
    bitDepth = args.videobitdepth
    outputPath = args.output_path

    print("*****Starting qcsetup*****")
    with progressbar.ProgressBar(max_value=4) as qcsetupBar:
        qcsetupBar.update(0)
        standardDF = qcsetup.setVideoBitDepth(bitDepth)
        qcsetupBar.update(1)
        qcsetup.inputCheck(inputPath)
        qcsetupBar.update(2)
        outputLocation = qcsetup.outputCheck(inputPath, outputPath)
        qcsetupBar.update(3)
        inputFileType = qcsetup.setInputFileType(inputPath)
        qcsetupBar.update(4)
    print("*****qcsetup Complete*****")

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
