import pandas as pd
from bs4 import BeautifulSoup 


file = open("/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml")
contents = file.read()

soup = BeautifulSoup(contents, 'xml')
framevalues = {}
framedata = {}

for frames in soup.find_all('frame'):
    frametime = frames.get('pkt_pts_time')
    taglist = frames.find_all('tag')

    for tag in taglist:
        tagkey = tag.get('key')
        tagvalue = tag.get('value')
        framedata['frametime'] = frametime
        framedata[tagkey] = tagvalue
    