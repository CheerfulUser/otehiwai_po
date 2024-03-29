# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 04:42:37 2022

@author: porri
"""

import os
import numpy as np
from math import isnan


def rough_exptime(mag, a=14.71317761, b=-17.04790805, c=18.22621702):
    exp_time = a * np.exp(mag + b) + c
    return int(exp_time)


def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def get_today():
    from datetime import datetime, timezone
    d = datetime.now(timezone.utc)
    date = f"{d.year:04.0f}{d.month:02.0f}{d.day:02.0f}"
    return date


def save_targs(target_list, name):
    import json
    with open(name, 'w') as fout:
        json.dump(target_list, fout, indent=2)


def make_obs_entry(exptime, filt, repeats, obj, ra, dec, propid, magnitude, rate="N/A", priority=1, exptype='object'):
    if isnan(float(magnitude)):
        magnitude = -9999
    obs = {
        "count": repeats,
        "expType": exptype,
        "object": obj,
        "filter": filt,
        "expTime": exptime,
        "ra": ra,
        "dec": dec,
        "magnitude": int(float(magnitude)),
        "rate": rate,
        "propid": propid,
        "priority": int(priority)
    }
    return obs

# print(get_today())
