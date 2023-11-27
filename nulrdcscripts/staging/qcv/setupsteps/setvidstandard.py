import pandas as pd
import os

path8Bit = "nulrdcscripts\staging\qcv\data\Video8BitValues.csv"
path10Bit = "nulrdcscripts\staging\qcv\data\Video10BitValues.csv"

csv8Bit = os.path.join(os.path.dirname(os.path.abspath(__file__)), path8Bit)
csv10Bit = os.path.join(os.path.dirname(os.path.abspath(__file__)), path10Bit)


def setvideobitdepthstandards(bitDepth):
    if bitDepth == 8:
        standardsDF = buildDF8Bit(csv8Bit)
    elif bitDepth == 10:
        standardsDF = buildDF10Bit(csv10Bit)
    return standardsDF


def buildDF8Bit(csv8Bit):
    standardsDF = pd.read_csv(csv8Bit, sep=",", index_col="criteria")
    return standardsDF


def buildDF10Bit(csv10Bit):
    standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    return standardsDF


# loccriteria = "ylow"
# value = "BRNGOut"
# standardsDF = buildDF8Bit(csv8Bit)
# standardsDF = standardsDF.loc[loccriteria, value]
# print(standardsDF)
