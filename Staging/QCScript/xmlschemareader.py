
import xmlschema 
from bs4 import BeautifulSoup
from pprint import pprint
schema= xmlschema.XMLSchema("/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/ffprobe.xsd")
file = "/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml"

print("Validating Schema")
schema.validate(file)
print("Schema Validated")



print("Decoding Schema")
data=schema.decode(file)
print("Decoded Schema")
print("Done")

pprint(schema.to_dict ('/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml'))

with open(file, 'r') as file:
    content=file.readlines()
content = "".join(content)
bs_content = BeautifulSoup(content,"xml")
videoframedata = 
