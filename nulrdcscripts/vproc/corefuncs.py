import progressbar
import subprocess
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

def two_pass_h264_encoding(pFile,audioStreamCounter,aFile):
    with progressbar.ProgressBar(max_value=100) as h264prog:
        
        for t in range(100):
            copyMixCommand = ["-c:a","aac","-b:a","256k"]
            fourto3Mixcommand = ["-filter_complex","[0:a:0][0:a:1]amerge=inputs=2[a]", "-map", "0:v", "-map", "[a]","-map","0:a:2","-map","0:a:3",]
            fourto2Mixcommand = ["-filter-complex","[0:a:0][:0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]","-map","0:v", "-map","[a]", "-map", "[b]",]
            twoto1Mixcommand = ["-filter-complex","[0:a:0][0:a:1]amerge=inputs=2[a]","-map","0:v","-map","[a]",]
            inputvideocommand = ["-y","-i",pFile,"-c:v","libx264","-preset","medium",'-b:v","8000k',"-pix_fmt","yuv420p"]
            h264prog.update(t)
            # create ffmpeg command
            if os.name == "nt":
                nullOut = "NUL"
            else:
                nullOut="/dev/null"
            pass1 = [args.ffmpeg.path]
            if not args.verbose:
                pass1 += ["-loglevel", "error"]
            pass1 += [inputvideocommand,
                "-pass",
                "1",
            ]
            
            h264prog.update(t)
            if audioStreamCounter > 0:
                if args.mixdown == "copy":
                    pass1 += copyMixCommand
                if args.mixdown == "4to3" and audioStreamCounter == 4:
                    pass1 += fourto3Mixcommand
                if args.mixdown == "4to2" and audioStreamCounter == 4:
                    pass1 += fourto2Mixcommand
                if args.mixdown == "2to1" and audioStreamCounter == 2:
                    pass1 += twoto1Mixcommand
            h264prog.update(t)
            pass1 += ["-f", "mp4", nullOut]
            pass2 = [args.ffmpeg_path]
            if not args.verbose:
                pass2 += ["-loglevel", "error"]
            pass2 += [inputvideocommand,
                "-pass",
                "2",
            ]
            if audioStreamCounter > 0:
                if args.mixdown == "copy":
                    pass2 += copyMixCommand
                if args.mixdown == "4to3" and audioStreamCounter == 4:
                    pass2 += fourto3Mixcommand
                if args.mixdown == "4to2" and audioStreamCounter == 4:
                    pass2 += fourto2Mixcommand
                if args.mixdown == "2to1" and audioStreamCounter == 2:
                    pass2 += twoto1Mixcommand
            pass2 += [aFile]
            h264prog.update(t)
            subprocess.run(pass1)
            h264prog.update(t)
            subprocess.run(pass2)
