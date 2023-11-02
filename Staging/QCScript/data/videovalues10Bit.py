tenBitVideoValues = {
    "YMIN": 0, 
    "YLOW": 64, 
    "YAVG": 512,
    "YHIGH": 940, 
    "YMAX": 1023, 
    "UMIN": 0, 
    "ULOW": 64, 
    "UAVG": 512,
    "UHIGH": 960,
    "UMAX": 1023,
    "VMIN": 0,
    "VLOW": 64,
    "VAVG": 512,
    "VHIGH": 960,
    "VMAX": 1023,
    "SATMIN": 0,
    "SATLOW": 181.02,
    "SATAVG": 362.04,
    "SATHIGH": 512,
    "SATMAX": 724.08,
    "TOUTMAX": 0.009,
    "VREPMAX": 0.03,
    "BRNGMAX": 1
}

tenBitVideo = {
    "YLOW": {'BRNGOut':64, 'clipping':0},
    "YHIGH": {'BRNGOut':940, 'clipping':1023},
    "YAVG": 512,
    "ULOW":{'BRNGOut':64, 'clipping':0},
    "UHIGH":{'BRNGOut':960, 'clipping':1023},
    'VLOW': {'BRNGOut':64, 'clipping':0},
    'VHIGH': {'BRNGOut':960, 'clipping': 1023},
    'VAVG': {'lowend':341, 'highend':682},
    'TOUTMAX': {'ideal': 0.009, 'MAX':0.009},
    'VREP': {'ideal':0, 'MAX':0.03},
    'BRNG': {'ideal':0, 'MAX':1}, 
    'SAT75' : {'lowend':0, 'highend':354.8}, #good
    'SAT100': {'lowend':354.8, 'highend':472.8}, #moderate
    'SATIllegal': {'lowend': 472.8, 'highend':724.08}, #critical
    "MSEf": {'ideal':0}, # close to zero as possible
    "PSNRideal": {'lowend':30, 'highend':50},
    "PSNRMax": {'low': 0, "high": 60}
}