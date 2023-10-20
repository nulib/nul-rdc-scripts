import os
import csv

from VideoScript.SetUp.AssignOutputDirectory import outdir as outdir


def write_output_csv(outdir, csvHeaderList, csvWriteList, output_metadata, qcResults):
    csv_file = os.path.join(outdir, "qc_log.csv")
    csvOutFileExists = os.path.isfile(csv_file)

    with open(csv_file, "a") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        if not csvOutFileExists:
            writer.writerow(csvHeaderList)
        writer.writerow(csvWriteList)
