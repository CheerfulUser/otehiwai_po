# -*- coding: utf-8 -*-
"""
Created on Wed Dec 6 22:02:07 2023

@author: kasou
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
import os
from utilly import *

package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

def scrub_yse_list(dec_lim=15):
    yses = pd.read_html('https://ziggy.ucolick.org/static/yse_latest.html')
    # found this link by inspecting the yse home page
    
    yse_df = yses[0]
    decs = np.array([int(v.split(':')[0]) for v in yse_df['Dec'].values]) #dec vals
    dec_ind = decs < dec_lim
    yse_df = yse_df.iloc[dec_ind]
    
    return yse_df

#yse_df = scrub_yse_list()

def make_yse_entries(yse_df, priority=1, exptime=[300], readout=40, filters=['g','r']):
    obs = []
    for index, row in yse_df.iterrows():
        repeats = 1
        ra = row['RA']
        ra = ra.strip().replace(':', ' ')
        dec = row['Dec']
        dec = dec.strip().replace(':', ' ')
        name = row['Name']
        magnitude = row['Discovery Mag']
        propid = '' #change this
        
        #making the ra and dec into decimal degrees
        c = SkyCoord(ra,dec,unit=(u.hourangle,u.deg))
        ra = c.ra.deg 
        dec = c.dec.deg

        for exp in exptime: 
            for f in filters:
                ob = make_obs_entry(exp, f, repeats, name, ra, dec, propid, magnitude, priority=priority)
                obs.append(ob)
    return obs


def make_yse_list():
    date = get_today()

    save_path = package_directory + 'targets/' + date
    make_dir(save_path)
    
    df = scrub_yse_list()
    yse = make_yse_entries(df)

    save_targs(yse, save_path + '/yse.json')
    print('!!! Made yse target list for ' + date + ' !!!')
    
if __name__ == '__main__':
    make_yse_list()
    
