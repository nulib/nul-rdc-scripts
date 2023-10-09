import xmlschema
import json

xml_document = '/Users/dcstaff/Documents/GitHub/nul-rdc-scripts/Staging/QCScript/vlc-record-2023-10-05-11h16m25s-test_NONEVIDEOSETTING_QTUNCOMPRESSED-p - Copy.mkv-.avi.qctools.xml'
print(json.dumps(xmlschema.to_dict(xml_document),indent=4))