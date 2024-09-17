import os
from nulrdcscripts.tools.checksoftware import main as checksoftwaremain
from nulrdcscripts.tools.spectrogramgeneration import main as spectrogramgenerationmain
from nulrdcscripts.tools.md5generation import main as md5generationmain
from nulrdcscripts.vproc2.params import args

software_check=[args.ffmpeg_path,args.ffprobe_path]
filetypes=["mkv","mp4"]
for i in software_check:
    checksoftwaremain(i)


def checkfolder (input_dir):
    folderTF = os.path.isdir(input_dir)
    if folderTF:
        pass
    else:
        raise Exception ("The given input path is not a folder. Please provide a folder location.")
    

def output_dir():
    if args.output_path:
        if os.path.isdir(args.output_path):
            pass
        else:
            print ("The output location provided is not a directory. Using the input directory")
            output_path =args.input_path
    else:
        print("Using input directory as the output location")
        output_path = args.input_path
    return output_path
        
    
def runBatch(input_path,output_path):
    for dirname in os.listdir(input_path):
        if os.path.isdir(dirname):
            runSingle(dirname,output_path)
        else:
            pass
        
def runSingle(input_path,output_path):
    for filename in input_path:
        if filename.endswith(filetypes):
            md5generationmain.md5generationCall(filename)
            spectrogramgenerationmain.generatespectrogramsCall(filename,output_path,args.ffprobe_path)
        else:
            pass

        


def main ():
    input_path= args.input_dir
    checkfolder(input_path)
    output_path = output_dir()

    if args.batch:
        runBatch(input_path,output_path)
    else:
        runSingle(input_path,output_path)