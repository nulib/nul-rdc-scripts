import os
from OutputCheck import outdir
from InputCheck import indir

for ffv1 in glob.glob1(indir, "*.mkv"):
    inputAbsPath = os.path.join(indir, ffv1Filename)
    baseFilename = ffv1Filename.replace ('.mkv','')
    baseOutput = os.path.join(outdir, baseFilename)
    pmOutputFolder = os.path.join(baseOutput, pm_identifier)
    framemd5File = baseFilename + '.framemd5'
    framemd5AbsPath = os.path.join (pmOutput Folder, framemd5File)
    acOutputFolder = os.path.join (acOutputFolder, baseFilename, + '-' + ac_identifier + '.mp4')
    metaOutputFolder = os.path.join(baseOutput, metadata_identifier)
    jsonAbsPath = os.path.join(metaOutputFolder, baseFilename + '-' + metadata_identifier + '.json')
    pmMD5Abspath = os.path.join (pmOutputFolder, baseFilename + '.md5')