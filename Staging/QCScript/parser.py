import pandas as pd
from io import BytesIO

file = "/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/test_NONEVIDEOSETTING_QTUNCOMPRESSED-p.mkv.qctools.xml"
with open (file,'rb') as xml:
    filexml = BytesIO(xml.read())

df = pd.read_xml(filexml),
xpath = "//frames"
df