#!/usr/bin/env python3

def equipment_dict():

    '''
    VTRs
    '''
    panasonic_10518 = {
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video'],
        'NU Tag' : '10518',
        'Equipment info' : 'Panasonic AG-1980'
    }

    sony_10516 = {
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video'],
        'NU Tag' : '10516',
        'Equipment info':'Sony SVO-5800'
    }

    sony_vo9800 = {
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video'],
        'NU Tag': '95095',
        'Equipment info':'Sony VO-9800'
    }

    sony_uvw1800 ={
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video']
    }

    pioneer_dvl919 ={
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video']
    }

    panasonic_ajd2390h = {
        'Coding Algorithm' : 'A=ANALOG',
        'Output is one of' : ['Composite', 'S-Video']
    }
    



    '''
    TBCs
    '''


    dps_295 = {
    'Coding Algorithm' : 'A=ANALOG',
    'Hardware Type' : 'TBC',
    'Output is one of' : ['Composite', 'S-Video', 'Component']
    }

    fa_510 = {
    'Coding Algorithm' : 'A=ANALOG',
    'Hardware Type' : 'TBC',
    'Output is one of' : ['Composite', 'S-Video', 'Component']
    }



    '''
    ADCs
    '''
    hd10ava_10519 = {
    'Coding Algorithm' : 'A=SDI',
    'Hardware Type' : 'A/D'
    }
   


    '''
    Capture Cards
    '''
    decklinkstudio4k = {
        'Coding Algorithm' : 'A=v210',
        'Hardware Type' : 'DIO'
    }
        
    equipment_dict = {
    'Panasonic LP Rack 1' : panasonic_10518, 
    'DPS TBC Rack 1' : dps_295,
    'FA-510 Rack 2' : fa_510,
    'AJA Rack 1' : hd10ava_10519,

    'Black Magic Rack 1' : decklinkstudio4k,
    'Sony SVHS Rack 1' : sony_10516,
    'Sony Betacam' : sony_uvw1800,
    'Sony VO-9800' : sony_vo9800,
    'Pioneer DVL-919' : pioneer_dvl919,
    'Panasonic AJ-D230H' : panasonic_ajd2390h


    }

    return equipment_dict
