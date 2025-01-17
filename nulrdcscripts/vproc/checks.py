#!/usr/bin/env python3


def inventory_check(item_csvDict):
    if item_csvDict is None:
        print("unable to locate file in csv data!")
        inventoryCheck = "FAIL"
    else:
        print("item found in inventory")
        inventoryCheck = "PASS"
    return inventoryCheck


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
