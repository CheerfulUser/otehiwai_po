# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 04:47:09 2022

@author: porri
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from copy import deepcopy
import os
from utilly import *
import requests


package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

# def get_target_list():
#     call = 'wget "https://docs.google.com/spreadsheets/d/1UFuei-xAv3a5rdKUBIArvL8RI1Vp9Hk54JiDwtYpYnA/export?format=csv&gid=0" -O "{}swope.csv"'.format(package_directory)

#     os.system(call)

#     df = pd.read_csv('swope.csv')
#     df = df.rename(columns={'Unnamed: 2':'name'})
#     df = df.dropna(how='all')

#     call = 'rm -rf {}swope.csv'.format(package_directory)
#     os.system(call)
#     return df

def get_target_list():
    # call = 'wget "https://docs.google.com/spreadsheets/d/1UFuei-xAv3a5rdKUBIArvL8RI1Vp9Hk54JiDwtYpYnA/export?format=csv&gid=0" -O "{}swope.csv"'.format(package_directory)
    
    URL = "https://docs.google.com/spreadsheets/d/1UFuei-xAv3a5rdKUBIArvL8RI1Vp9Hk54JiDwtYpYnA/export?format=csv&gid=0"
    
    test = requests.get(URL)
    open(package_directory + 'swope.csv', 'wb').write(test.content)

    df = pd.read_csv(package_directory + 'swope.csv')
    df = df.rename(columns={'Unnamed: 2':'name'})
    df = df.dropna(how='all')

    # call = 'rm -rf {}debass.csv'.format(package_directory)
    # os.system(call)
    return df

def sort_targets(sn):
    misc_s = np.where(sn['name'].values == 'Active Other SN Ia Targets')[0][0]
    hst_s = np.where(sn['name'].values == 'HST')[0][0]
    hst_pos_s =  np.where(sn['name'].values == 'HST possible')[0][0]
    other_s = np.where(sn['name'].values == 'Other Active Targets')[0][0]
    misc = sn.iloc[misc_s+1:hst_s]
    hst = sn.iloc[hst_s+1:hst_pos_s]
    hst_pos = sn.iloc[hst_pos_s+1:other_s]

    return misc, hst, hst_pos

def make_swope_entries(df,priority,exptime=180,readout=40,filters=['V']):
    obs = []
    for j in range(len(df)):
        l = df.iloc[j]
        repeats = 1
        ra = l.RA
        dec = l.Dec
        print(l['name'])
        name = l['name'] + '_22S02'
        for f in filters:
            ob = make_obs_entry(exptime,f,repeats,name,ra,dec,propid='2022S-02',priority=priority)
            obs += [ob]
    return obs    

def make_swope_list():
    date = get_today()

    save_path = package_directory + 'targets/' + date

    make_dir(save_path)
    df = get_target_list()
    targs = sort_targets(df)
    priorities = [1,2,3]
    swope = []
    for i in range(len(targs)):
        swope += make_swope_entries(targs[i],priorities[i])

    save_targs(swope,save_path + '/swope.json')
    print('!!! Made Swope target list for ' + date + ' !!!')


if __name__ == '__main__':
    make_swope_list()