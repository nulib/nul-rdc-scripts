import os

def mediaconch_policy_exists(policy_path):
    if not os.path.isfile(policy_path):
        print ("Unable to Find Mediaconch Policy:", policy_path)
        print ("Check if file exists before running")
        quit()