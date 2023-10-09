import glob
import os
from lxml import etree


def file_path_validation(filepath):
    try:
        filepath.endswith (".xml")
        return (True)
    except:
        try:
            os.path.isdir(filepath)
            try: 
                glob.glob(filepath, '*.csv')
                return (False)
            except: 
                raise Exception ("There are no XML files in this directory")
        except:
            raise Exception ("Your input is not a valid XML file or directory")