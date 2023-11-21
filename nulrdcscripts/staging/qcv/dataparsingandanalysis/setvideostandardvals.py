import pandas as pd
from pandasgui import show


csv8Bit = "nulrdcscripts\staging\qcv\data\Video8BitValues.csv"
csv10Bit = "nulrdcscripts\staging\qcv\data\Video10BitValues.csv"
bitDepth = 10


def setvideobitdepthstandards(bitDepth):
    if bitDepth == 8:
        standardsDF = buildDF8Bit()
    elif bitDepth == 10:
        standardsDF = buildDF10Bit()
    show(standardsDF)


def buildDF8Bit():
    standardsDF = pd.read_csv(csv8Bit, sep=",")
    return standardsDF


def buildDF10Bit():
    standardsDF = pd.read_csv(csv10Bit, sep=",")
    return standardsDF


setvideobitdepthstandards(bitDepth)
