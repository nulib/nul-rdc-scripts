import pandas as pd

df = pd.read_csv("testdata.csv")

# Not legit values just testing the method before inputting into actual script
dfYHIGHErrors = df.query("YHIGH == 608.0")

dfYHIGHErrorsCount = len(dfYHIGHErrors.index)


# col=df["YLOW"]
# YLOWError = col[np.abs(col) == 130]

print(dfYHIGHErrorsCount)
