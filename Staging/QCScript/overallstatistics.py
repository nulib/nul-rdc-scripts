import pandas as pd


# Forms dictionaries of the summary data from Pandas
def videodatastatistics(videodata):
    videogeneralstats = {}
    videostats = videodata.describe()
    videogeneralstats["videostats"] = videostats
    return videogeneralstats


def audiodatastatistics(audiodata):
    audiogeneralstats = {}
    audiostats = audiodata.describe()
    audiogeneralstats["audiostats"] = audiostats
    return audiogeneralstats
