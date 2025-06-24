import os
import progressbar
import pandas as pd
from nulrdcscripts.vqc.params import args
from nulrdcscripts.vqc import dataparsing
from nulrdcscripts.vqc import qcsetup
from nulrdcscripts.vqc import overallStatistics
from nulrdcscripts.vqc import output

template_path = os.path.join(os.path.dirname(__file__), "data", "templateVideo.txt")

if not os.path.exists(template_path):
    print(f"Template not found at: {template_path}")
    # Optionally, raise an error or exit


def main():
    inputPath = os.path.normpath(args.input_path)
    bitDepth = args.videobitdepth
    outputPath = args.output_path

    print("*****Starting qcsetup*****")
    with progressbar.ProgressBar(max_value=4) as qcsetupBar:
        qcsetupBar.update(0)
        qcsetup.inputCheck(inputPath)
        qcsetupBar.update(1)
        outputLocation = qcsetup.outputCheck(inputPath, outputPath)
        qcsetupBar.update(2)
        inputFileType = qcsetup.setInputFileType(inputPath)
        qcsetupBar.update(3)
    print("*****qcsetup Complete*****")

    print("*****Parsing File Video*****")
    if inputFileType == "JSON":
        print("Parsing video JSON...")
        videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
    else:
        print("Parsing video XML...")
        videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
        outputdata = outputLocation + "/video_data.csv"
        videodata.to_csv(outputdata, index=False)
    print("*****Parsing complete*****")

    print("*****Generating Full Video Descriptive Statistics*****")
    videoDSDF = dataparsing.videodatastatistics(videodata)
    # audioDSDF = dataparsing.audiodatastatistics(audiodata)

    def test_bitdepth_medians(videoDSDF):

        # Extract the median values
        y = videoDSDF.loc["50%", "ybitdepth"]
        u = videoDSDF.loc["50%", "ubitdepth"]
        v = videoDSDF.loc["50%", "vbitdepth"]

        # Check if all are 8 or all are 10
        assert (y == u == v == 8) or (
            y == u == v == 10
        ), f"Median bit depths are not all 8 or all 10: y={y}, u={u}, v={v}"

    print("***Determining Video Bit Depth Standards***")
    test_bitdepth_medians(videoDSDF)
    videobitdepth = videoDSDF["ybitdepth"].mode()[0]
    standardDF = qcsetup.setVideoBitDepth(videobitdepth)

    # Determine output directory
    if outputPath == "input":
        outputDir = os.path.dirname(inputPath)
    else:
        outputDir = outputPath

    sumVideoStatsCSV = dataparsing.videostatstocsv(videoDSDF, outputDir)
    # sumAudioStatsCSV = dataparsing.audiostatstocsv(audioDSDF, outputDir)
    print("*****Generated Full Video Descriptive Statistics*****")

    print("*****Analysing Full Video Descriptive Statistics*****")
    errors = overallStatistics.runstatsvideo(videoDSDF, standardDF)

    # Determine pass/fail status
    passfail_video = "PASS" if not errors else "FAIL"

    all_criteria = [
        "ylow",
        "yhigh",
        "ulow",
        "uhigh",
        "vlow",
        "vhigh",
    ]  # or however you define all checks
    output.write_video_stats_to_txt(
        errors,
        template_path,  # use the variable above
        outputDir + "/video_stats.txt",
        videobitdepth,
        os.path.basename(inputPath),
        passfail_video,
        all_criteria,
        videoDSDF,
        standardDF,
    )


if __name__ == "__main__":
    main()
