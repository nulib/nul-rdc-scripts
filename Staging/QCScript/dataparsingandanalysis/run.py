import setup
import file
import folder
from argparser import args

inputPath = args.input_path
outputPath = args.output_path
videobitdepth = args.videobitdepth

videoBitDepth = setup.setVideoBitDepth(videobitdepth)

#filepath = input("Filepath")
fileType = setup.inputCheck(inputPath)

if fileType == "Folder":
    folder(inputPath, videoBitDepth)
elif fileType == "File":
    file(inputPath, videoBitDepth)

savePath = setup.outputCheck(outputPath, inputPath)

