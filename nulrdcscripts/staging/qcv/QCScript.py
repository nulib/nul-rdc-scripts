import videoanalysis.fbyfYUV as fbyfYUV
import setupsteps.setup as setup
import setupsteps.setvidstandard as setvidstandard

videoBitDepth = setup.setVideoBitDepth("--10bit")
videoBitDepth = setvidstandard.setvideobitdepthstandards(videoBitDepth)
videodata = "data\data.txt"

errors = fbyfYUV.checkerrors(videodata, videoBitDepth)
