import videoanalysis.fbyfYUV as fbyfYUV
from setupsteps import setup, setvidstandard

videoBitDepth = setup.setVideoBitDepth("--10bit")
videoBitDepth = setvidstandard.setvideobitdepthstandards(videoBitDepth)
videodata = "data\data.txt"

errors = fbyfYUV.checkerrors(videodata, videoBitDepth)
