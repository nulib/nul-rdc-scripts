import pandas as pd


# Gathers general video data for summary report
def videodatastatistics(videodata):
    videostats = videodata.describe()
    return videostats

# Outputs summary video stats as a dictionary - which will be used for comparison analysis
def videostatstodict (videostats):
    summarydatavideodict = videostats.to_dict()
    return summarydatavideodict

#Outputs summary video stats as a csv
def videostatstocsv (videostats):
    summarydatavideocsv = videostats.to_csv("videosummarystats.csv", index=True)
    return summarydatavideocsv

#Gathers general audio data for summary report
def audiodatastatistics(audiodata):
    audiodata = audiodata.describe()
    return audiodata

#Output summary audio stats as dictionary - which will be used for comparison analysis
def audiostatstodict (audiostats):
    summarydataaudiodict = audiostats.to_dict()
    return summarydataaudiodict

#Output summary audio stats as a csv
def audiostatstocsv (audiostats):
    summarydataaudiocsv = audiostats.to_csv("audiosummarystats.csv", index = True)
    return summarydataaudiocsv
   


