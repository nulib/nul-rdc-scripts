import pandas as pd
from bs4 import BeautifulSoup 
import matplotlib as mpl

file = open("/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml")
contents = file.read()

soup = BeautifulSoup(contents, 'xml')
framevalues = {}
framedata = {}
framedataonly = {}
tagkeylist = []

for frames in soup.find_all('frame'):
    frametime = frames.get('pkt_pts_time')
    taglist = frames.find_all('tag')
    framedata['frametime'] = frametime
    for tag in taglist:
        tagkey = tag.get('key')
        tagvalue = tag.get(str('value'))
        datapoint = tagkey + ':' + tagvalue
        framedataonly[tagkey] = tagvalue
        tagkeylist=tagkey
        framedata['datapoint']=datapoint
        framedata[frametime]=framedataonly
        df = pd.DataFrame(framedata, columns=[tagkeylist])
        df
    
    