#!/usr/bin/env python3

"""
Helper functions to handle warnings for aqc.
"""

from operator import itemgetter
from itertools import *
import nulrdcscripts.aqc.helpers as helpers

def group(timestamps: list, pt_time: float, cooldown: float, min_length: int = 0):

    """
    Takes a list of timestamps and groups them into single warnings.
    This way you arent just bombarded with too many warnings.

    :param list timestamps: list of frames where a warning occurs
    :param float pt_time: length in seconds of a frame
    :param float cooldown: minimum length apart in seconds for warnings to be separate
    :param float min_length: minimum length in frames for a warning to be counted
    :return: list of warnings, each warning is a list of frames
    :rtype: list[list]
    """

    # create groups of consecutive frames
    groups = []
    for k, g in groupby(enumerate(timestamps), lambda x: x[0]-x[1]):
        groups.append(list(map(itemgetter(1), g)))

    if not groups:
        return []
    
    # remove any groups that are too short
    long_groups = []
    for group in groups:
        if len(group) >=  min_length:
            long_groups.append(group)
    groups = long_groups

    # merge close groups together
    merged_groups = []
    cooldown_frames = int(cooldown/pt_time)
    last_end = -cooldown_frames
    # for every group, add it as new group if its far enough away form the last
    # merge it into last group if they are close enough
    for group in groups:
        if group[0] - last_end < cooldown_frames:
            merged_groups[-1].extend(group)
        else:
            merged_groups.append(group)
        last_end = group[-1]

    groups = merged_groups
    
    return groups

def parse(groups: dict[str: list], pt_time: float, cooldown: float):

    """
    Parse the groups warning frames into a readable dict.

    :param dict groups: dictionary of warnings where the key is the label+a number and the value is the list of frames
    :param float pt_time: length of frame in seconds
    :param float cooldown: length of cooldown in seconds
    :return: readable warnings
    :rtype: dict
    """

    if not groups:
        return

    warnings = {}

    # add a readable warning for every group
    for key in groups:
        start_sec = pt_time * groups[key][0]
        end_sec = pt_time * groups[key][-1]
        # format times
        start_time = helpers.sec2time(start_sec)
        end_time = helpers.sec2time(end_sec)

        # take out the number at the end of the key since its not necessary in the readable dict
        # this number is important since no 2 keys can be the same
        label = ''.join([i for i in key if not i.isdigit()])
        # for short durations, treat the clipping as a single event
        if end_sec - start_sec <= cooldown:
            warnings.update({start_time: label})
        else:
            warnings.update({start_time + " - " + end_time: label})

    # print()
    return warnings