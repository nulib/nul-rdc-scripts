import videoanalysis.fbyfYUV as fbyfYUV
import setupsteps.setup as setup

videoBitDepth = setup.setVideoBitDepth("--10bit")
videodata = "data\data.txt"
errors = fbyfYUV.checkerrors(videodata, videoBitDepth)
