#!/usr/bin/env python3

from operator import itemgetter
from itertools import *
import nulrdcscripts.aqc.helpers as helpers

def group(timestamps, pt_time, cooldown, min_length=0):

    # create groups of consecutive frames
    groups = []
    for k, g in groupby(enumerate(timestamps), lambda x: x[0]-x[1]):
        groups.append(list(map(itemgetter(1), g)))

    if not groups:
        return []
    
    long_groups = []
    for group in groups:
        if len(group) >=  min_length:
            long_groups.append(group)

    groups = long_groups

    merged_groups = []
    cooldown_frames = int(cooldown/pt_time)
    last_end = -cooldown_frames
    for group in groups:
        #print(group)
        if group[0] - last_end < cooldown_frames:
            merged_groups[-1].extend(group)
        else:
            merged_groups.append(group)
        last_end = group[-1]

    groups = merged_groups
    
    return groups

def parse(groups, pt_time, cooldown):

    if not groups:
        return

    warnings = {}

    for key in groups:
        start_sec = pt_time * groups[key][0]
        end_sec = pt_time * groups[key][-1]
        # format times
        start_time = helpers.sec2time(start_sec)
        end_time = helpers.sec2time(end_sec)

        label = ''.join([i for i in key if not i.isdigit()])
        # for short durations, treat the clipping as a single event
        if end_sec - start_sec <= cooldown:
            warnings.update({start_time: label})
        else:
            warnings.update({start_time + " - " + end_time: label})

    # print()
    return warnings