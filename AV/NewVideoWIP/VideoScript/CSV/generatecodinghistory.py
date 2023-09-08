from Dictionaries import equipmentDict as equipment_dict


def generate_coding_history(coding_history, hardware, append_list):
    '''
    Formats hardware into BWF style coding history. Takes a piece of hardware (formatted: 'model; serial No.'), splits it at ';' and then searches the equipment dictionary for that piece of hardware. Then iterates through a list of other fields to append in the free text section. If the hardware is not found in the equipment dictionary this will just pull the info from the csv file and leave out some of the BWF formatting.
    '''
    equipmentDict = equipment_dict.equipment_dict()
    if hardware.split(';')[0] in equipmentDict.keys():
        hardware_history = equipmentDict[hardware.split(';')[0]]['''Coding 
                                                                 Algorithm'''] + ',' + 'T=' + hardware
        for i in append_list:
            if i:
                hardware_history += '; '
                hardware_history += i
        if 'Hardware Type' in equipmentDict.get(hardware.split(';')[0]):
            hardware_history += '; '
            hardware_history += equipmentDict[hardware.split(';')[0]]['Hardware Type']
        coding_history.append(hardware_history)
    #handle case where equipment is not in the equipmentDict using a more general format
    elif hardware and not hardware.split(';')[0] in equipmentDict.keys():
        hardware_history = hardware
        for i in append_list:
            if i:
                hardware_history += '; '
                hardware_history += i
        coding_history.append(hardware_history)
    else:
        pass
    return coding_history
