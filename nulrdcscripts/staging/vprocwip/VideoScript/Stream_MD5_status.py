def stream_md5_status(input_streammd5, output_streammd5):
    if output_streammd5 == input_streammd5:
        print("Stream checksums match. Your file is lossless")
        streamMD5status = "PASS"
    else:
        print("Stream checksums do not match. Your output file may not be lossless")
        streamMD5status = "FAIL"
    return streamMD5status
