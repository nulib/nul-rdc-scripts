import file
import folder
from argparser import args
from setupsteps import setup

inputPath = args.input_path
outputPath = args.output_path
videobitdepth = args.videobitdepth

videoBitDepth = setup.setVideoBitDepth(videobitdepth)
videoBitDepth = setup.setvideobitdepthstandard(videoBitDepth)


# filepath = input("Filepath")
fileType = setup.inputCheck(inputPath)


def runPathType(fileType, inputPath, videoBitDepth):
    if fileType == "Folder":
        inventory_input = folder.runBulkFolder(inputPath, videoBitDepth)
    elif fileType == "File":
        inventory_input = file.runIndividualFile(inputPath, videoBitDepth)
    return inventory_input


runPathType(fileType, inputPath, videoBitDepth)

savePath = setup.outputCheck(outputPath, inputPath)
