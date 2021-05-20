#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import datetime
import shutil
import glob
from dpx2ffv1parameters import args
import corefuncs
import dpx2ffv1supportfuncs

#TO DO: general clean up (improve readability by separating out some functions); merge avfuncs scripts between different transcode scripts where overlapping functions exist and separate format specific functions better

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

#set up the input, output, and other folder/file sctructure elements
#expected folder/file structure is input/title/subfolder_identifier/title_0000001.dpx
indir = corefuncs.input_check()
outdir = corefuncs.output_check()
#TO DO: allow running without subfolder identifier to support having the dpx files directly in the title folder?
#set the subfolder_identifier. Defaults to 'pm' if not specified
if not args.subfolder_identifier:
    subfolder_identifier = 'pm'
else:
    subfolder_identifier = args.subfolder_identifier

#set a limit so that the command only runs on title folders containing the string specified
limit = dpx2ffv1supportfuncs.assign_limit()
title_list = dpx2ffv1supportfuncs.get_immediate_subdirectories(indir)
if args.filter_list:
    with open(args.filter_list) as f:
        filter_list = set(line.rstrip() for line in f)

    title_list = [item for item in title_list if item in filter_list]

checklist = []
for title in title_list:
    if not limit or (limit) in title:
        #currently the input folder name is fixed as input/title/pm for consistency in the structure of the RAWcooked data
        if os.path.isdir(os.path.join(indir, title, subfolder_identifier)):
            #TO DO: differentiate subfolder_identifier and dpx_subfolder_identifier
            title_abspath = os.path.join(indir, title)
            indirbase = os.path.join(title_abspath, subfolder_identifier)
            outpathbase = os.path.join(outdir, title)
            outpathfull = os.path.join(outpathbase, subfolder_identifier)
            ffv1_name = os.path.join(title + '_' + subfolder_identifier + '.mkv')
            framemd5_name = os.path.join(title + '_' + subfolder_identifier + '.framemd5')
            mkv_abspath = os.path.join(outpathfull, ffv1_name)
            framemd5_abspath = os.path.join(outpathfull, framemd5_name)
            #TO DO: it may be better to make the default behavior be to just run rawcooked on title
            #then you could add a flag where you specify pm folders if they exist

            #TO DO check for md5 file in dpx folders
            #if not found, generate and output to input folder

            print('\n'"***Processing", title + "***" + '\n')

            #gather system metadata
            osinfo = platform.platform()
            ffvers = corefuncs.get_ffmpeg_version()
            rawcvers = corefuncs.get_rawcooked_version()
            tstime = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            #build and execute rawcooked command
            rawcooked_command = [args.rawcooked_path, '--all', '--framemd5', '--framemd5-name', framemd5_abspath]
            if args.framerate:
                rawcooked_command += ['-framerate', args.framerate]
            rawcooked_command += [indirbase, '-o', mkv_abspath]
            #print(rawcooked_command)
            rawcooked_results = subprocess.check_output(rawcooked_command).decode("ascii").rstrip()

            #log transcode finish time
            tftime = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            #if output exists, create an md5checksum
            if os.path.isfile(mkv_abspath):
                mkvhash = dpx2ffv1supportfuncs.hashlib_md5(mkv_abspath)
            else:
                mkvhash = None
            #write md5 checksum to md5 file
            with open (os.path.join(outpathfull, title + '_' + subfolder_identifier + '.md5'), 'w',  newline='\n') as f:
                print(mkvhash, '*' + ffv1_name, file=f)

            data = {}
            data[title] = []
            metadict = { 'system information': {
            'operating system': osinfo,
            'ffmpeg version': ffvers,
            'rawcooked version': rawcvers,
            'transcode start time': tstime,
            'transcode end time': tftime
            }}

            attachments = dpx2ffv1supportfuncs.list_mkv_attachments(mkv_abspath)
            format_metadict = dpx2ffv1supportfuncs.get_mkv_format_metadata(mkv_abspath)
            video_metadict = dpx2ffv1supportfuncs.get_mkv_video_metadata(mkv_abspath)
            audio_metadict = dpx2ffv1supportfuncs.get_mkv_audio_metadata(mkv_abspath)
            #note that the size is output in bytes.  This can be converted to MiB by dividing by 1024**2 or GiB by dividing by 1024**3
            dpxsize = dpx2ffv1supportfuncs.get_folder_size(os.path.join(indir, title, subfolder_identifier))
            #log ffv1 (folder) size
            mkvsize = dpx2ffv1supportfuncs.get_folder_size(outpathfull)
            pm_runtime = format_metadict.get('format')['duration']
            post_transcode_dict = { 'post-transcode metadata': {
            'filename': ffv1_name,
            'md5 checksum': mkvhash,
            'duration' : pm_runtime,
            'streams' : format_metadict.get('format')['nb_streams'],
            'compressed size': mkvsize,
            'uncompressed size': dpxsize
            }}
            video_dict = {'video': {
            'video streams': [stream.get('codec_name') for stream in (video_metadict['streams'])],
            'framerate': [stream.get('r_frame_rate') for stream in (video_metadict['streams'])][0],
            'width': [stream.get('width') for stream in (video_metadict['streams'])][0],
            'height': [stream.get('height') for stream in (video_metadict['streams'])][0],
            'sample_aspect_ratio': [stream.get('sample_aspect_ratio') for stream in (video_metadict['streams'])][0],
            'display_aspect_ratio': [stream.get('display_aspect_ratio') for stream in (video_metadict['streams'])][0],
            'pixel format': [stream.get('pix_fmt') for stream in (video_metadict['streams'])][0]
            }}
            audio_dict = {'audio': {
            'audio codecs': [stream.get('codec_long_name') for stream in (audio_metadict['streams'])],
            'audio bitrate': [stream.get('bits_per_raw_sample') for stream in (audio_metadict['streams'])],
            'audio sample rate': [stream.get('sample_rate') for stream in (audio_metadict['streams'])],
            'audio channels': [stream.get('channels') for stream in (audio_metadict['streams'])]
            }}
            data_dict = {'data': {
            'attachments': attachments
            }}
            output_technical_metadata = {'technical metadata': [video_dict, audio_dict, data_dict]}
            post_transcode_dict.update(output_technical_metadata)
            metadict.update(post_transcode_dict)
            data[title].append(metadict)
            with open(os.path.join(outpathfull, title + '_pm.json'), 'w', newline='\n') as outfile:
                json.dump(data, outfile, indent=4)

            #compare runtimes between the ac and pm files
            #TO DO - write to csv file in base output directory rather than txt file
            if args.check_runtime:
                #It may be a good idea to format the runtime outputs as sets or lists
                ac_runtime = dpx2ffv1supportfuncs.grab_runtime(title_abspath, 'ac', 'mp4')
                #pm_runtime = dpx2ffv1supportfuncs.grab_runtime(outpathbase, subfolder_identifier, 'mkv')

                with open(os.path.join(indir, os.path.join(outpathfull, 'verification_log.txt')), 'a',  newline='\n') as f:
                    print(rawcooked_results, file=f)
                    print('\n'"Access Copy Runtime:", file=f)
                    print(ac_runtime, file=f)
                    print('\n'"Preservation Master Runtime:", file=f)
                    print(pm_runtime, file=f)

        elif not os.path.isdir(os.path.join(indir, title, 'pm')):
            print('no pm folder in input directory')
    elif limit and not (limit) in title:
        print(title, 'does not contain ', limit)

#TO DO - replace verification check with simply writing PASS/FAIL outputs to a CSV file
if checklist:
    print("* * * * * * * * * * * * * * * * *" + '\n' + "Checking verification log results" + '\n' + "* * * * * * * * * * * * * * * * *")
    for i in checklist:
        dpx2ffv1supportfuncs.verification_check(i)

#if args.verifylossless:
    #for *.mkv run ffprobe to check if file contains a rawcooked reversibility file
    #if so, funnel into rawcooked decode pathway

#TO DO - move this to supportfuncs and rewrite it for the new version of rawcooked
if args.decodeffv1:
    indir = corefuncs.input_check()
    outdir = corefuncs.output_check()
    limit = dpx2ffv1supportfuncs.assign_limit()
    corefuncs.input_check(indir)

    #TO DO: make sure terminology is consistent across script (i.e. title vs object_folder)
    for object_folder in os.listdir(indir):
        dpxverifolder = os.path.join(outdir, object_folder, object_folder + '_dpx')
        #TO DO: add check for more than one mkv file
        if not limit or (limit) in object_folder:
            if os.path.isdir(os.path.join(indir, object_folder)):
                print ('\n', "FOLDER: ", os.path.join(object_folder))
                mkv_file = glob.glob1(os.path.join(indir, object_folder, 'pm'), "*.mkv")
                mkvcounter = len(mkv_file)
                if mkvcounter == 1:
                    for i in mkv_file:
                        ffv1_file_abspath = os.path.join(indir, object_folder, 'pm', i)
                        mkvsize = dpx2ffv1avfuncs.get_folder_size(os.path.join(indir, object_folder, 'pm'))
                        subprocess.call([args.rawcooked_path, ffv1_file_abspath, '-o', dpxverifolder])
                        #may want to allow passing an md5 file or md5 data into dpx_md5_compare so that the md5 doesn't have to be embedded
                        dpxsize = dpx2ffv1avfuncs.get_folder_size(os.path.join(dpxverifolder, 'pm'))
                        #compareset, orig_md5list = dpx2ffv1avfuncs.dpx_md5_compare(os.path.join(dpxverifolder, 'pm'))
                        print ("mkv folder size:", mkvsize)
                        print ("DPX folder size:", dpxsize)
                elif mkvcounter < 1:
                    print ("No mkv files found in", os.path.join(indir, object_folder))
                elif mkvcounter > 1:
                    print ("More than 1 mkv file found in", os.path.join(indir, object_folder))
        elif limit and not (limit) in object_folder:
            print("Skipped", object_folder)
