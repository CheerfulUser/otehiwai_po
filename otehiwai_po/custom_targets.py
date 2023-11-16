#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 04:03:40 2023

@author: hopkinsm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from copy import deepcopy
import os
from utilly import save_targs, get_today, make_dir, make_obs_entry
import requests
from astroquery.mpc import MPC

package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

# maybe use
def make_custom_entries(df,priority,exptime=180,readout=40,filters=['V']):
    obs = []
    for j in range(len(df)):
        l = df.iloc[j]
        repeats = 1
        ra = l.RA
        dec = l.Dec
        print(l['name'])
        name = l['name'] + '_22S02'
        magnitude = l['Disc. Mag.']
        for f in filters:
            ob = make_obs_entry(exptime,f,repeats,name,ra,dec,propid='2022S-02',priority=priority, magnitude=magnitude)
            obs += [ob]
    return obs    


def make_custom_entries(targets):
    """This largely copies make_look_entries. COme back and add bells and 
    whistles after fixing them in look and swope"""
    obs = []
    for targ in targets:
        eph = MPC.get_ephemeris(targ['name'], location='474', number=1)
        # add bells and whistles here
        ob = make_obs_entry(exptime=targ['exptime'],
                            filt=targ['filter'],
                            repeats=targ['repeats'],
                            obj=targ['name'],
                            ra=eph['RA'][0],
                            dec=eph['Dec'][0],
                            propid='',
                            magnitude=eph['V'],
                            priority=1,
                            exptype='object')
        obs += [ob]
    return obs    

def make_custom_list(targets):
    """Input targets as list of dictionaries containing:
    name recognised by MPC,
    filter to observe in
    exposure time
    and repeats.
    Uses astroquery to get current ra,dec and makes json from this.
    
    to add: Exposure calculation based on mag? see look and swope scripts
    
    Nota bene:
    Current system of getting ra,dec of object at time of executing script isn't
    great, as observation could be carried out 12 hours later and comets move.
    This is the same as the system to get the LOOK targets so is probably fine,
    but potential for error in both of these should be kept in mind.
    In short, don't trust the ra,dec given for a NEO.
    """
    date = get_today()

    save_path = package_directory + 'targets/' + date

    make_dir(save_path)
    
    custom_entries = make_custom_entries(targets)

    save_targs(custom_entries,save_path + '/custom.json')
    print('Made custom target list for ' + date + '.')


if __name__ == '__main__':
    make_custom_list()