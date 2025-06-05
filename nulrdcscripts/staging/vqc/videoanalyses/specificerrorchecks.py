# Checks for TBC errors

def checkVideoGainError ():
    pass
    # will use the Y AVG (range?) and look for dramatic peaks

def checkChrominanceNoiseBW ():
    pass
    # will use the U and V readings to make sure that this is at zero as this is solely for BW video

def checkColorDropout ():
    pass
    # will use the U and V readings to make sure that there is activity. Solely for color video

def checkChrominanceNoiseColor ():
    pass
    # will look for abrupt spikes in Min and Max values for UV

def checkLuminanceNoise ():
    pass
    # will use the BRNG and TOUT values & Y High and Low. 

# Checks for mechanical errors

def checkTrackingError ():
    pass
    # will use TOUT and VREP (VREP rules out color errors)

def checkVideoHeadClog ():
    pass
    # will use PSNRf and MSEf along with the YUV difference. Lower PSNRf, higher MSEf, and large difference and prolonged spikes in YUV

# Checks for tape damage

def checkDropouts ():
    pass
    # VREP and TOUT

def standardChecks ():
    checkVideoGainError()
    checkLuminanceNoise()
    checkTrackingError()
    checkVideoHeadClog()
    checkDropouts()

def checkBWVideo():
    checkChrominanceNoiseBW()
    standardChecks()

def checkColorVideo ():
    checkChrominanceNoiseColor()
    checkColorDropout()
    standardChecks()