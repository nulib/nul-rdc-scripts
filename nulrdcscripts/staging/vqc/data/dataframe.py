import pandas as pd

csv = "Video8BitValues.csv"

df = pd.read_csv(csv, index_col="criteria")
criteriaToCheck = "brngout"
criteria = "uhigh"
extraction = df.at[criteria, criteriaToCheck]

print(extraction)
