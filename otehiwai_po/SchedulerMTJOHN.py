# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 03:30:03 2022

@author: porri
"""

from astroplan import Observer
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord

from astroplan import ObservingBlock
from astroplan.constraints import TimeConstraint
from astropy import units as u
from astroplan.constraints import AtNightConstraint, AirmassConstraint
from astroplan.scheduling import Transitioner

from astroplan.scheduling import SequentialScheduler
from astroplan.scheduling import Schedule
from astroplan import FixedTarget
from astroplan.scheduling import PriorityScheduler

from glob import glob
import json 

from utilly import *
# from datetime import date
import os
package_directory = os.path.dirname(os.path.abspath(__file__)) + '\\'

def make_target(ra,dec,name):
    c = SkyCoord(ra,dec,unit=u.deg)
    targ = FixedTarget(coord=c,name=name)
    return targ

def make_block(obj,priority,readout):

    read_out = readout * u.second

    targ = make_target(obj['ra'],obj['dec'],obj['object'])
    exp = obj['expTime'] * u.s
    repeats = obj['count']
    filt = obj['filter']


    block = ObservingBlock.from_exposures(targ, priority, exp, repeats, read_out,
                                          configuration = {'filter': filt})
    return block


def MOA_transitioner(slew_rate=0.5,RV=180,I=240):

    slew_rate = slew_rate*u.deg/u.second # need to measure
    transitioner = Transitioner(slew_rate,
                                {'filter':{('R','V'): RV*u.second,
                                        ('I','V'): I*u.second,
                                        ('I','R'): I*u.second,
                                        'default': 180*u.second}}) # need to measure

    return transitioner

def BC_transitioner(slew_rate=0.5,RV=3,I=3):

    slew_rate = slew_rate*u.deg/u.second # need to measure
    transitioner = Transitioner(slew_rate,
                                {'filter':{('R','V'): RV*u.second,
                                        ('I','V'): I*u.second,
                                        ('I','R'): I*u.second,
                                        'default': 3*u.second}}) # need to measure

    return transitioner

def make_alt_plot(priority_schedule,save_path):
    import warnings
    warnings.filterwarnings("ignore")

    from astroplan.plots import plot_schedule_airmass
    # from astroplan.plots import light_style_sheet
    import matplotlib.pyplot as plt

    # plot the schedule with the airmass of the targets
    plt.figure(figsize = (14,6))
    
    plot_schedule_airmass(priority_schedule,show_night='True',use_local_tz=True)
    plt.legend(loc = "upper right")
    plt.savefig(save_path+'alt_plot.pdf')


def make_schedule(date,telescope):
    if date is None:
        date = get_today()
    date = str(date)
    print('ZAC:', date)
    
    print(package_directory + date)
    targets = glob(package_directory + 'targets\\' + date + '\\*.json' )
    # print(targets)
    blocks = []
    print(targets)
    for target in targets:
        print('!!!! ',target)
        targ = json.load(open(target))
        for ob in targ:
            if telescope.lower() == 'moa':
                blocks +=  [make_block(ob,priority=0,readout=80)]
            elif telescope.lower() == 'bc':
                blocks +=  [make_block(ob,priority=0,readout=5)]
    
    observatory = Observer.at_site(site_name='MJO')
    global_constraints = [AirmassConstraint(max = 2.5, boolean_constraint = False),
                      AtNightConstraint.twilight_civil()]
    if telescope.lower() == 'moa':
        transitioner = MOA_transitioner()
        sched_path = 'MOA'
    elif telescope.lower() == 'bc':
        transitioner = BC_transitioner()    
        sched_path = 'BC'
    else:
        m = 'No transitioner set'
        raise ValueError(m)


    dat = '{y}-{m}-{d}'.format(y=date[0:4],m=date[4:6],d=date[6:8])
    noon_before = Time(dat + ' 06:00')
    noon_after = Time(dat + ' 20:00')


    seq_scheduler = SequentialScheduler(constraints = global_constraints,
                                    observer = observatory,
                                    transitioner = transitioner)
    # Initialize a Schedule object, to contain the new schedule
    sequential_schedule = Schedule(noon_before, noon_after)

    # Call the schedule with the observing blocks and schedule to schedule the blocks
    seq_scheduler(blocks, sequential_schedule)

    prior_scheduler = PriorityScheduler(constraints = global_constraints,
                                    observer = observatory,
                                    transitioner = transitioner)
    # Initialize a Schedule object, to contain the new schedule
    priority_schedule = Schedule(noon_before, noon_after)

    # Call the schedule with the observing blocks and schedule to schedule the blocks
    # print(blocks)
    prior_scheduler(blocks, priority_schedule)

    table = priority_schedule.to_table()

    save_path = package_directory + 'obs_lists\\' + date + '\\'
    make_dir(save_path)

    table = table.to_pandas()
    table.to_csv(save_path + 'schedule.csv',index=False)

    make_alt_plot(priority_schedule,save_path)


if __name__ == '__main__':
    date=None
    Tele =['moa', 'bc']
    # T = 'moa'
    # for T in Tele:
    make_schedule(date, telescope = 'moa')