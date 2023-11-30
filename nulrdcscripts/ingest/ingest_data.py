#!/usr/bin/env python3

"""
Contains lists and dictionaries used in Ingest_Sheet_Maker class

:role_dict: default rules for assigning roles to files
:x_extension_dict: rules for identifying x by file extension
:x_parse_dict: rules for identifying x by filename patterns
:header_names: header names used in ingest csv file
:pattern_dict: patterns used to identify sides, regions, etc.
"""

# Contains default rules for assigning roles to files.
role_dict = {
    "framemd5": {
        "identifiers": [".framemd5"],
        "type": "extension",
        "role": "S",
        "label": "framemd5 file",
        "file_builder": "_supplementary_",
    },
    "metadata": {
        "identifiers": [".xml", ".json", ".pdf"],
        "type": "extension",
        "role": "S",
        "label": "technical metadata file",
        "file_builder": "_supplementary_",
    },
    "qctools": {
        "identifiers": [".xml.gz", ".qctools.mkv"],
        "type": "extension",
        "role": "S",
        "label": "QCTools report",
        "file_builder": "_supplementary_",
    },
    "logfile": {
        "identifiers": [".log"],
        "type": "extension",
        "role": "S",
        "label": "log file",
        "file_builder": "_supplementary_",
    },
    "spectrogram": {
        "identifiers": ["spectrogram"],
        "type": "pattern",
        "role": "S",
        "label": "spectrogram file",
        "file_builder": "_supplementary_",
    },
    "dpx_checksum": {
        "identifiers": ["dpx.txt"],
        "type": "extension",
        "role": "S",
        "label": "original DPX checksums",
        "file_builder": "_supplementary_",
    },
    "access": {
        "identifiers": [
            "-a.",
            "_a.",
            "-am.",
            "_am.",
            "_am_",
            "-am-",
            "-am_",
            "_access",
        ],
        "type": "pattern",
        "role": "A",
        "label": None,
        "file_builder": "_access_",
    },
    "preservation": {
        "identifiers": [
            "-p.",
            "_p.",
            "-pm.",
            "_pm",
            "_pm_",
            "-pm-",
            "-pm_",
            "_preservation",
        ],
        "type": "pattern",
        "role": "P",
        "label": None,
        "file_builder": "_preservation_",
    },
}
x_extension_dict = {
    "auxiliary": {
        "identifiers": [".jpg", ".JPG"],
        "type": "extension",
        "role": "X",
        "label": "image",
        "file_builder": "_auxiliary_",
    }
}
# Contains rules for assigning x files based on filename patterns.
x_parse_dict = {
    "front": {
        "identifiers": ["Front."],
        "type": "pattern",
        "role": "X",
        "label": "asset front",
        "file_builder": "_auxiliary_",
    },
    "back": {
        "identifiers": ["Back."],
        "type": "pattern",
        "role": "X",
        "label": "asset back",
        "file_builder": "_auxiliary_",
    },
    "asset": {
        "identifiers": ["_Asset", "-Asset"],
        "type": "pattern",
        "role": "X",
        "label": "asset",
        "file_builder": "_auxiliary_",
    },
    "can": {
        "identifiers": ["_Can", "-Can"],
        "type": "pattern",
        "role": "X",
        "label": "can",
        "file_builder": "_auxiliary_",
    },
    "ephemera": {
        "identifiers": ["_Ephemera", "-Ephemera"],
        "type": "pattern",
        "role": "X",
        "label": "ephemera",
        "file_builder": "_auxiliary_",
    },
}

# Contains header names used in the ingest sheet csv file.
header_names = [
    "work_type",
    "work_accession_number",
    "file_accession_number",
    "filename",
    "description",
    "label",
    "role",
    "work_image",
    "structure",
]

# Contains patterns to be identified in filenames and their corresponding meaning
# side 1 is denoted by s01, etc.
pattern_dict = {
    "side": "s(\d{2})",
    "part": "p(\d{2})",
    "region": "r(\d{2})",
    "capture": "c(\d{2})",
}