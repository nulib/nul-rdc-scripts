import pandas as pd
def importSelectCSV(inventory):
    input_csv=pd.read_csv(inventory)
    vTR=input_csv['VTR']


def generate_coding_history(coding_history,hardware,append_list):
    pass

def openInventory(input_folder):
    for i in input_folder:
        if i.endswith(".csv") and "inventory" in i:
            inventory=i
            break
        else:
            raise Exception("There is no CSV file found in the given folder. CSV file must contain the word 'inventory'")
    return inventory