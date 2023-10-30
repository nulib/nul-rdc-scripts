import setup
import file
import folder
from argparser import args

inputPath = args.input_path
outputPath = args.output_path
#filepath = input("Filepath")
fileType = setup.inputCheck(inputPath)

if fileType == "Folder":
    folder(inputPath)
elif fileType == "File":
    file(inputPath)

savePath = setup.outputCheck(outputPath, inputPath)

