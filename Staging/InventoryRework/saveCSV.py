import os


def opencsv(csvfilename):
    open_CSV = "" + "start EXCEL.exe" + "" + csvfilename
    os.system(open_CSV)
