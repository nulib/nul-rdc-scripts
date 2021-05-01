#!/usr/bin/env python3

import os
import sys
import hashlib
import subprocess
import platform
import json
import datetime
import glob
import shutil
import posixpath
from dpx2ffv1parameters import args

def assign_limit():
    if args.textlimit:
        limit = args.textlimit
    else:
        limit = None
    return limit

def get_immediate_subdirectories(folder):
    '''
    get list of immediate subdirectories of input
    '''
    return [name for name in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, name))]

def hashlib_md5(filename):
    '''
    Uses hashlib to return an MD5 checksum of an input filename
    '''
    read_size = 0
    last_percent_done = 0
    chksm = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        while True:
            #2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write('[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = chksm.hexdigest()
    return md5_output
#this function is from the IFI's scripts with a minor change
#open(str(filename)), 'rb') as f has been changed to open(filename, 'rb') as f

def get_folder_size(folder):
    '''
    Calculate the folder size
    '''
    total_size = 0
    d = os.scandir(folder)
    for entry in d:
        try:
            if entry.is_dir():
                total_size += get_folder_size(entry.path)
            else:
                total_size += entry.stat().st_size
        except FileNotFoundError:
            #file was deleted during scandir
            pass
        except PermissionError:
            return 0
    return total_size

'''
#use mediainfo instead of ffprobe (?)
def dpx2ffv1_ffprobe_report(input_abspath):
        video_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=codec_name,avg_frame_rate,codec_time_base,width,height,pix_fmt,codec_tag_string', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
        audio_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_name,codec_time_base,codec_tag_string', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
'''

def list_mkv_attachments(input_file_abspath):
    #could also identify with -select streams m:filename
    t_probe_out = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 't', '-show_entries', 'stream_tags=filename', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    tags = [streams.get('tags') for streams in (t_probe_out['streams'])]
    attachment_list = []
    for i in tags:
        filename = [i.get('filename')]
        attachment_list.extend(filename)
    return attachment_list

def get_mkv_video_metadata(input_file_abspath):
    ffprobe_command = [args.ffprobe_path, '-v', 'error', '-select_streams', 'v',]
    ffprobe_command += ['-show_entries', 'stream=codec_name,width,height,pix_fmt,sample_aspect_ratio,display_aspect_ratio,r_frame_rate']
    ffprobe_command += [input_file_abspath, '-of', 'json']
    video_meta_out = json.loads(subprocess.check_output(ffprobe_command).decode("ascii").rstrip())
    return video_meta_out

def get_mkv_audio_metadata(input_file_abspath):
    ffprobe_command = [args.ffprobe_path, '-v', 'error', '-select_streams', 'a',]
    ffprobe_command += ['-show_entries', 'stream=codec_long_name,bits_per_raw_sample,sample_rate,channels']
    ffprobe_command += [input_file_abspath, '-of', 'json']
    audio_meta_out = json.loads(subprocess.check_output(ffprobe_command).decode("ascii").rstrip())
    return audio_meta_out

def get_mkv_format_metadata(input_file_abspath):
    ffprobe_command = [args.ffprobe_path, '-v', 'error']
    ffprobe_command += ['-show_entries', 'format=duration,nb_streams']
    ffprobe_command += [input_file_abspath, '-of', 'json']
    format_meta_out = json.loads(subprocess.check_output(ffprobe_command).decode("ascii").rstrip())
    return format_meta_out

def dpx_md5_compare(dpxfolder):
    '''
    Returns two sets
    One from the original DPX sequence's md5 checksum
    The other from the calculated checksums of the decoded DPX sequence
    '''
    md5list = []
    orig_md5list = {}
    for i in os.listdir(dpxfolder):
        abspath = os.path.join(dpxfolder, i)
        if i.endswith(".md5"):
            orig_md5list = set(map(str.strip, open(abspath)))
        elif i.endswith(".xml"):
            pass
        else:
            y = hashlib_md5(abspath)
            filehash = y + ' *' + i
            md5list.append(filehash)
    compareset = set(md5list)
    return compareset, orig_md5list

def grab_runtime(folder, subfolder_identifier, filetype):
    '''
    Look for an ac folder containing an video file of specified type
    If found, return the runtime
    '''
    itemfolder = os.path.join(folder, subfolder_identifier)
    if os.path.isdir(itemfolder):
        videofile = glob.glob1(itemfolder, '*.' + filetype)
        filecounter = len(videofile)
        if filecounter == 1:
            for i in videofile:
                file_abspath = os.path.join(itemfolder, i)
                runtime = subprocess.check_output([args.ffprobe_path, '-v', 'error', file_abspath, '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1']).decode("ascii").rstrip()
                #this returns the total runtime in seconds
        elif filecounter < 1:
            runtime = "no " + filetype + "files found in " + itemfolder
        elif filecounter > 1:
            runtime = "more than 1 file found with extension " + filetype
    else:
        runtime = "no " + subfolder_identifier + "folder found"
    return runtime
    #when comparing runtimes, you could check if this value is a float, which would allow you to know if there was an error here
'''
def verification_check(folder):
    verifile = os.path.join(folder, 'pm', "verification_log.txt")
    if not os.path.isfile(verifile):
        print('No verification_log.txt file found in', folder)
    else:
        with open(verifile) as f:
            data = f.read().split('\n')
            if 'Entries in original checksum not found in calculated checksum:' in data:
                checksums1 = data[data.index('Entries in original checksum not found in calculated checksum:') +1]
            if 'Entries in calculated checksum not found in original checksum:' in data:
                checksums2 = data[data.index('Entries in calculated checksum not found in original checksum:') +1]
            print(data[0])
            if not 'None' in checksums1:
                print('\t'"Entries found in the original checksum not found in calculated checksum", '\n''\t'"  See verification log for details")
            if not 'None' in checksums2:
                print('\t'"Entries found in the calculated checksum not found in original checksum", '\n''\t'"  See verification log for details")
            if 'Access Copy Runtime:' in data:
                try:
                    ac_runtime = float(data[data.index('Access Copy Runtime:') +1])
                except ValueError:
                    ac_runtime = None
            else:
                ac_runtime = "not logged"
            if 'Preservation Master Runtime:' in data:
                try:
                    pm_runtime = float(data[data.index('Preservation Master Runtime:') +1])
                except ValueError:
                    pm_runtime = None
                    print ("pm runtime is not a float")
            else:
                pm_runtime = "not logged"
            if ac_runtime and pm_runtime and not "not logged" in [ac_runtime] and not "not logged" in [pm_runtime]:
                runtime_total = ac_runtime - pm_runtime
                if abs(runtime_total) > 0.01 or not 'None' in checksums1 or not 'None' in checksums2:
                    if runtime_total > 0.01:
                        print('\t'"Access copy is", runtime_total, "seconds longer than FFV1 file")
                    elif runtime_total < -0.01:
                        print('\t'"Access copy is", abs(runtime_total), "seconds shorter than FFV1 file")
            elif pm_runtime and not ac_runtime:
                print('\t'"ac runtime is not a float")
            elif not pm_runtime and not ac_runtime:
                print('\t'"ac and pm runtimes are not floats")
            elif "not logged" in pm_runtime and "not logged" in ac_runtime:
                print('\t'"ac and pm runtimes were not logged")
            elif "not logged" in pm_runtime and not "not logged" in ac_runtime:
                print('\t'"pm runtime was not logged")
            elif not "not logged" in pm_runtime and "not logged" in ac_runtime:
                print('\t'"ac runtime was not logged")
'''
