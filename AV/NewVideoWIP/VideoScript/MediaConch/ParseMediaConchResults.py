def parse_mediaconchResults(mediaconchResults_dict):
    if "FAIL" in mediaconchResults_dict.values():
        mediaconchResults="FAIL"
        failed_policies=[]
        for key in mediaconchResults_dict.keys():
            failed_policies.append(key)
        mediaconchResults=(mediaconchResults + ': ' + 
                           str(failed_policies).strip('[]'))
    else:
        mediaconchResults="PASS"
        return mediaconchResults