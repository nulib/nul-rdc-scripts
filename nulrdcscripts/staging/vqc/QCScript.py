import videoanalyses.fbyfYUV as fbyfYUV
from setupsteps import setup

videoBitDepth = setup.setVideoBitDepth("--10bit")
videoBitDepth = setup.setvideobitdepthstandard(videoBitDepth)
videodata = "data\data.txt"

errors = fbyfYUV.checkerrors(videodata, videoBitDepth)
