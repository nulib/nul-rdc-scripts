import os
import setup
from argparser import args
from progress.bar import Bar

inputPath = os.path.normpath(args.input_path)
outputPath = os.path.normpath(args.output_path)
bitDepth = args.videobitdepth


print("*****Starting Setup*****")
standardDF = setup.setVideoBitDepth(bitDepth)
inputPath = setup.inputCheck(inputPath)
outputPath = setup.outputCheck(inputPath, outputPath)
