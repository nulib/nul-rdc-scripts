import os
import json
import validation
import dataparsing

filepath = input("File path to xml file(s)")

validation.file_path_validation(filepath)

if filepath:
    dataparsing.xml_file_given_set(filepath)
else:
    dataparsing.directory_given_set(filepath)
