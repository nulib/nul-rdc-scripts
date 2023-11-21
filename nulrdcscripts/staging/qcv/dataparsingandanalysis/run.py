import setup
import file
import folder
from argparser import args

inputPath = args.input_path
outputPath = args.output_path
videobitdepth = args.videobitdepth

videoBitDepth = setup.setVideoBitDepth(videobitdepth)

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
