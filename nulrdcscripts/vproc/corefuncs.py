
from nulrdcscripts.vproc.params import args




def parse_mediaconchResults(mediaconchResults_dict):
    if "FAIL" in mediaconchResults_dict.values():
        mediaconchResults = "FAIL"
        failed_policies = []
        for key in mediaconchResults_dict.keys():
            if "FAIL" in mediaconchResults_dict.get(key):
                failed_policies.append(key)
        mediaconchResults = mediaconchResults + ": " + str(failed_policies).strip("[]")
    else:
        mediaconchResults = "PASS"
    return mediaconchResults


def stream_md5_status(input_streammd5, output_streammd5):
    if output_streammd5 == input_streammd5:
        print("stream checksums match.  Your file is lossless")
        streamMD5status = "PASS"
    else:
        print("stream checksums do not match.  Output file may not be lossless")
        streamMD5status = "FAIL"
    return streamMD5status