import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from copy import deepcopy
import os
from utils import *

package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

def get_target_list():
    call = 'wget "https://docs.google.com/spreadsheets/d/1JPIAXjcy-maVeNMkImRHFnhfoo2ulJQzHkCJOL0AbKs/export?format=csv&gid=0" -O "{}debass.csv"'.format(package_directory)

    os.system(call)

    df = pd.read_csv('debass.csv')
    follow_ind = df['Following?'].values == 'YES'
    df = df.iloc[follow_ind]

    call = 'rm -rf {}debass.csv'.format(package_directory)
    os.system(call)
    return df


def make_debass_entries(debass,exptime=300,readout=40,filters=['R','V']):
    obs = []
    for j in range(len(debass)):
        l = debass.iloc[j]
        repeats = 1
        ra = l.RA
        dec = l.DEC
        name = l['snid'] + '2022S-05'
        priority = l['priority']
        for f in filters:
            ob = make_obs_entry(exptime,f,repeats,name,ra,dec,propid='2022S-05',priority=priority)
            obs += [ob]
    return obs    
            

def debas_priority(debass,names=None):
    
    debass['priority'] = int(1)

    if names is not None:
        for i in range(len(names)):
            name = names[i]
            for j in range(len(debass)):
                if name[0] in debass.iloc[j]['Target Name']:
                    debass['priority'].iloc[j] = int(name[1])

    return debass


def make_debass_list(name_priority=None):
    date = get_today()

    save_path = package_directory + 'targets/' + date

    make_dir(save_path)

    df = get_target_list()
    df = debas_priority(df,names = name_priority)
    debass = make_debass_entries(df)
    save_targs(debass,save_path + '/debass.json')
    print('!!! Made DEBASS target list for ' + date + ' !!!')


if __name__ == '__main__':
    make_debass_list()