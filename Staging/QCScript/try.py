import pandas as pd
from bs4 import BeautifulSoup 
from tabulate import tabulate
import json
file = open("/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml")
contents = file.read()
soup = BeautifulSoup(contents, 'xml')
framevalues = {}
framesdata = {}
framedatapoint = {}
tagkeylist = []
tagvalueslist = []
filename = 'filename.csv'
for frames in soup.find_all('frame'):
    taglist = frames.find_all('tag')
    frametime = frames.get('pkt_pts_time')
    for frame in frametime:
        for tag in taglist:
            tagkey = tag.get('key')
            def tagkeycleaning (tagkey):
                tagkeyclean1 = tagkey.replace('lavfi.astats','')
                tagkeyclean2 = tagkeyclean1.replace('lavfi.', '')
                tagkeyclean3 = tagkeyclean2.replace('signalstats.','')
                tagkeyclean4 = tagkeyclean3.replace('.',' ')
                cleanedtagkey = tagkeyclean4.replace('_',' ')
                return cleanedtagkey
            cleankey=tagkeycleaning(tagkey)
            tagvalue = tag.get(str('value'))
            framedatapoint[cleankey] = tagvalue
    
        framesdata[frametime] = framedatapoint
    with open('test.json','w') as fp:
        json.dump(framesdata, fp)

'''
    df = pd.DataFrame.from_dict(framesdata, orient='index')

    df.to_csv(filename, encoding = 'utf-8',sep =',')
    '''