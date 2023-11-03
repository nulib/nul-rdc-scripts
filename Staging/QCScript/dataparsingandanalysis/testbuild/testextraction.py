import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues

df = pd.read_csv("testdata.csv")

# Not legit values just testing the method before inputting into actual script


# col=df["YLOW"]
# YLOWError = col[np.abs(col) == 130]


variables = ["LOW", "HIGH", "AVG"]


def lumaErrors(df, tenBitVideoValues):
    criticalerrors = {}
    moderateerrors = {}
    fine = {}
    for i in variables:
        criteria = "Y" + variables[i]
        if variables[i] == "LOW":
            standardvalue = tenBitVideoValues.get(criteria["BRNG"])
            equationBRNG = "" + criteria + "" + ">=" + standardvalue

            df = df.query(equationBRNG)

    subDF = df[["Frame", "Frame Time", "YHIGH"]]
    print(subDF)


lumaErrors(df, tenBitVideoValues)
