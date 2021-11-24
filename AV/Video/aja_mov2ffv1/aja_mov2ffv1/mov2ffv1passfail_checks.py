#!/usr/bin/env python3

def inventory_check(item_csvDict):
    if item_csvDict is None:
        print("unable to locate file in csv data!")
        inventoryCheck = "FAIL"
    else:
        print("item found in inventory")
        inventoryCheck = "PASS"
    return inventoryCheck

def parse_mediaconchResults(mediaconchResults_dict):
    if "FAIL" in mediaconchResults_dict.values():
        mediaconchResults = "FAIL"
        failed_policies = []
        for key in mediaconchResults_dict.keys():
            if "FAIL" in mediaconchResults_dict.get(key):
                failed_policies.append(key)
        mediaconchResults = mediaconchResults + ': ' + str(failed_policies).strip('[]')
    else:
        mediaconchResults = "PASS"
    return mediaconchResults

def stream_md5_status(input_streammd5, output_streammd5):
    if output_streammd5 == input_streammd5:
        print ('stream checksums match.  Your file is lossless')
        streamMD5status = "PASS"
    else:
        print ('stream checksums do not match.  Output file may not be lossless')
        streamMD5status = "FAIL"
    return streamMD5status

def lossless_check(input_metadata, output_metadata, streamMD5status):
    if output_metadata.get('output_techMetaA') == input_metadata.get('input_techMetaA') and output_metadata.get('output_techMetaV') == output_metadata.get('input_techMetaV'):
        QC_techMeta = "PASS"
    else:
        print("input and output technical metadata do not match")
        QC_techMeta = "FAIL"
        
    losslessCheckDict = {'technical metadata' : QC_techMeta, 'stream checksums' : streamMD5status}
    if "FAIL" in losslessCheckDict.values():
        losslessCheck = "FAIL"
        losslessFail = []
        for key in losslessCheckDict.keys():
            if "FAIL" in losslessCheckDict.get(key):
                losslessFail.append(key)
        losslessCheck = losslessCheck + ': ' + str(losslessFail).strip('[]')
    else:
        losslessCheck = "PASS"
    
    return losslessCheck