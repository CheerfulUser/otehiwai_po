import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from copy import deepcopy
import os
from utils import *


package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'


def scrub_look_targets(maglim=22, dec_lim=15):
    looks = pd.read_html('https://neoexchange.lco.global/lookproject/')
    active = looks[0]
    new = looks[1]
    mag_ind = (active['V Mag.'].values < 22) & (active['V Mag.'].values > 12)
    dec = np.array([int(v.split(' ')[0]) for v in active['Dec.'].values])
    dec_ind = dec < dec_lim
    active = active.iloc[mag_ind & dec_ind]
    mag_ind = new['V Mag.'].values < 22
    dec = np.array([int(v.split(' ')[0]) for v in new['Dec.'].values])
    dec_ind = dec < dec_lim
    new = new.iloc[mag_ind & dec_ind]
    look = {'active':active,'new':new}
    return look


def rate_limit(rate,pixsize=0.6,ap_size=5):
    pixrate = rate/pixsize
    time = (ap_size / pixrate) * 60
    return int(time)



def format_coord(ra,dec):
    if type(ra) == str:
        c = SkyCoord(ra,dec,unit=(u.hourangle,u.deg))
        ra = c.ra.deg
        dec = c.dec.deg
    return ra,dec


def round_look_exposures(exptime):
    allowed = np.array([20,30,60,120,300])
    diff = abs(allowed - exptime)
    ind = np.argmin(diff)
    return allowed[ind]



def make_look_entries(look,total_time=0.5*60**2,readout=40,filters=['R']):
    obs = []
    key = list(look.keys())
    for k in key:
        ll = look[k]
        for j in range(len(ll)):
            l = ll.iloc[j]
            rate_lim = rate_limit(l['Rate ("/min)'])
            exptime = rough_exptime(l['V Mag.'])
            if rate_lim < exptime:
                m = '!!! exposure time is too long for rate!!! \n Rescaling: {}s -> {}s'.format(exptime,rate_lim)
                print(m)
                exptime = rate_lim
            if 300 < exptime:
                m = '!!! exposure time is too long for tracking!!! \n Rescaling: {}s -> {}s'.format(exptime,500)
                print(m)
                exptime = 300
            exptime = int(round_look_exposures(exptime))
            repeats = int(total_time / (exptime + readout))
            ra,dec = format_coord(l['R.A.'],l['Dec.'])
            name = l['Target Name'].replace(' ','_').replace('/','') + '_' + '2022S-01'
            priority = l['priority']
            for f in filters:
                ob = make_obs_entry(exptime,f,repeats,name,ra,dec,propid='2022S-01',priority=priority)
                obs += [ob]
    return obs    
            

def look_priority(look,names=None,magrange=[['22-19',2],['19-17',3],['17-15',4],['15-12',5]]):
    looks = deepcopy(look['active'])
    looks['priority'] = int(3)
    if magrange is not None:
        for i in range(len(magrange)):
            f,b = magrange[i][0].split('-')
            b = float(b); f = float(f)
            if b > f:
                temp = deepcopy(f)
                f = b
                b = temp
            print(f,b)
            ind = (looks['V Mag.'].values < f) & (looks['V Mag.'].values > b)
            looks['priority'].iloc[ind] = int(magrange[i][1])


    if names is not None:
        for i in range(len(names)):
            name = names[i]
            for j in range(len(looks)):
                if name[0] in looks.iloc[j]['Target Name']:
                    looks['priority'].iloc[j] = int(name[1])
    look['active'] = looks
    return look



def make_look_list(name_priority=[['81P',1],['73P',1],['UN271',1]]):
    date = get_today()

    save_path = package_directory + 'targets/' + date

    make_dir(save_path)

    look = scrub_look_targets()
    look = look_priority(look,names=name_priority)
    looks = make_look_entries(look)
    save_targs(looks,save_path + '/look.json')

    print('!!! Made LOOK target list for ' + date + ' !!!')


if __name__ == '__main__':
    make_look_list()