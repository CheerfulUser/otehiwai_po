# -*- coding: utf-8 -*-
"""
Created on Thurs Nov 30 10:03:13 2023

@author: kasou
"""

import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os
from utilly import *

# this script makes a target list for reference images of every supernova
# observed in the 2022 summer run at MJO (for the purpose of difference
# imaging) - these were all taken on MOA so need the ref images taken on MOA too

package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

def get_target_list():
    df = pd.read_csv('2022sne_refimgs_targetlist.csv',  delimiter=';', 
                     names = ['name', 'ra', 'dec', 'filter', 'exp', 'discovery mag'] )
    df = df.dropna(how='all') #drops nan entries - shouldn't be any anyway

    return df

#df = get_target_list()

def make_refsne_entries(df, priority=2, readout=40):
    obs = []
    for index, row in df.iterrows():
        repeats = 1
        ra = row['ra']
        ra = ra.strip().replace('h', ' ').replace('m', ' ').replace('s', '')
        
        dec = row['dec']
        dec = dec.strip().replace('h', ' ').replace('m', ' ').replace('s', '')
        
        #making the ra and dec into decimal degrees
        c = SkyCoord(ra,dec,unit=(u.hourangle,u.deg))
        ra = c.ra.deg 
        dec = c.dec.deg
        
        #print(row['name'])
        name = row['name'] + '_ref'
        filt = row['filter']
        exptime = row['exp']
        propid = '_ref' #maybe change this not sure
        magnitude = row['discovery mag']
        
        ob = make_obs_entry(exptime, filt, repeats, name, ra, dec, propid, magnitude,priority=2)
        obs.append(ob)
    return obs

def make_refsne_list():
    date = get_today()

    save_path = package_directory + 'targets/' + date
    make_dir(save_path)
    df = get_target_list()
    sne = make_refsne_entries(df)

    save_targs(sne, save_path + '/refsne.json')
    print('!!! Made 2022 sne reference image target list for ' + date + ' !!!')



if __name__ == '__main__':
    make_refsne_list()
  
