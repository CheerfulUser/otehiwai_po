import os
import numpy as np

def rough_exptime(mag,a=14.71317761, b=-17.04790805,  c=18.22621702):
    exp_time = a*np.exp(mag+b) + c
    return int(exp_time)


def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def get_today():
    from datetime import datetime
    d = datetime.now()
    date = str(d.year) + str(d.month) + str(d.day)
    return date

def save_targs(target_list,name):
    import json
    with open(name, 'w') as fout:
        json.dump(target_list, fout,indent=2)

def make_obs_entry(exptime,filt,repeats,obj,ra,dec,propid,priority=1,exptype='object'):
    obs = {
        "count": repeats,
        "expType": exptype,
        "object": obj,
        "filter": filt,
        "expTime": exptime,
        "ra": ra,
        "dec": dec,
        "propid": propid,
        "priority":int(priority)
        }
    return obs