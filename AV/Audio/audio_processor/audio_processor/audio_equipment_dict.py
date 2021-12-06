#!/usr/bin/env python3

def equipment_dict():

    '''
    Decks
    '''
    yamaha_c300 = {
    'Coding Algorithm' : 'A=ANALOG'
    }

    '''
    ADCs
    '''
    mh_lio8 = {
    'Coding Algorithm' : 'A=PCM'
    }

    equipment_dict = {
        'Yamaha C300' : yamaha_c300,
        'Metric Halo LIO8' : mh_lio8
    }

    return equipment_dict
