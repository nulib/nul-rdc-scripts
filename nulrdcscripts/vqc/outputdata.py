import os 

def writetxtOS(summarystats,standard,outputfolder):
    outfilename=os.path.basename(outputfolder)+ '.txt'
    with open (outfilename,'w') as f:
        