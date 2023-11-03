import setup
import file
import folder
from argparser import args

inputPath = args.input_path
outputPath = args.output_path
videoBitDepth = args.videobitdepth

#filepath = input("Filepath")
fileType = setup.inputCheck(inputPath) # allows for either a file or a directory to be run

bitDepth = setup.setBitDepth(videoBitDepth) #selects which bit depth to calculate against

if fileType == "Folder":
    folder.run(inputPath, bitDepth)
elif fileType == "File":
    file.run(inputPath, bitDepth)

savePath = setup.outputCheck(outputPath, inputPath)

