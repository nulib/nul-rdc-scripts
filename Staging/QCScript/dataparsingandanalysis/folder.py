import dataparsing
import overallstatistics
import videoanalysis
import errortiers
import fbyfvideoanalysis
from argparser import args

folderpath = args.input_file
videobitdepth = args.videobitdepth

for file in folderpath:
     #Parses the raw XML into individual readings by frame (determined by frametime)
    videodata = dataparsing.dataparsingandtabulatingvideo(folderpath)
    audiodata = dataparsing.dataparsingandtabulatingaudio(folderpath)
    
	#Video analysis frame by frame
    fbferrors = fbyfvideoanalysis.checkerrors(videodata, videobitdepth)
    
	#Collects the video summary data - outputs CSV and Dictionary
    videostats = overallstatistics.videodatastatistics(videodata)

    videofeedtodict = overallstatistics.videostatstodict(videostats)
    videofeedtocsv = overallstatistics.videostatstocsv(videostats)

    #Collects the audio summary data - outputs CSV and Dictionary
    audiostats = overallstatistics.audiodatastatistics(audiodata)

    audiofeedtodict = overallstatistics.audiostatstodict(audiostats)
    audiofeedtocsv = overallstatistics.audiostatstocsv(audiostats)

    #Video analysis for summary report
    summaryvideoerrors = videoanalysis.checkAllVideo(videostats, videobitdepth)

	
    #Assigns errors to tiers for verbose reporting
    errortiers.errorsvideo(summaryvideoerrors)
