# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 03:30:03 2022

@author: porri
"""

import json
import os
from datetime import datetime, timezone
from glob import glob

from astroplan import FixedTarget
from astroplan import Observer
from astroplan import ObservingBlock
from astroplan.constraints import AtNightConstraint, AirmassConstraint
from astroplan.scheduling import PriorityScheduler
from astroplan.scheduling import Schedule
from astroplan.scheduling import Transitioner
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from utilly import make_dir, get_today

package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'


def make_target(ra, dec, name):
    c = SkyCoord(ra, dec, unit=u.deg)
    targ = FixedTarget(coord=c, name=name)
    return targ


def make_block(obj, readout):
    read_out = readout * u.second

    targ = make_target(obj['ra'], obj['dec'], obj['object'])
    exp = obj['expTime'] * u.s
    repeats = obj['count']
    filt = obj['filter']
    priority = obj['priority']
    magnitude = obj['magnitude']

    block = ObservingBlock.from_exposures(targ, priority, exp, repeats, read_out,
                                          configuration={'filter': filt, 'magnitude': magnitude})
    return block


def MOA_transitioner(slew_rate=0.5, RV=180, I=240):
    slew_rate = slew_rate * u.deg / u.second  # need to measure
    transitioner = Transitioner(slew_rate,
                                {'filter': {('R', 'V'): RV * u.second,
                                            ('I', 'V'): I * u.second,
                                            ('I', 'R'): I * u.second,
                                            'default': 180 * u.second}})  # need to measure

    return transitioner


def BC_transitioner(slew_rate=0.5, RV=3, I=3):
    slew_rate = slew_rate * u.deg / u.second  # need to measure
    transitioner = Transitioner(slew_rate,
                                {'filter': {('R', 'V'): RV * u.second,
                                            ('I', 'V'): I * u.second,
                                            ('I', 'R'): I * u.second,
                                            'default': 3 * u.second}})  # need to measure

    return transitioner


def make_alt_plot(priority_schedule, save_path):
    import warnings
    warnings.filterwarnings("ignore")

    from astroplan.plots import plot_schedule_airmass
    # from astroplan.plots import light_style_sheet
    import matplotlib.pyplot as plt

    # plot the schedule with the airmass of the targets
    plt.figure(figsize=(14, 6))

    plot_schedule_airmass(priority_schedule, show_night=True)
    plt.legend(loc="upper right")
    plt.savefig(save_path + 'alt_plot.pdf')


def add_exposure_details_to_table(priority_schedule, table):
    exposure_times = []
    repeats = []

    for slot in priority_schedule.slots:
        if hasattr(slot.block, 'target'):
            exposure_times.append(int(slot.block.time_per_exposure.value))
            repeats.append(int(slot.block.number_exposures))
        elif slot.block:
            exposure_times.append('')
            repeats.append('')

    table.add_column(exposure_times, name='exptime (s)')
    table.add_column(repeats, name="repeats")
    return table


def add_local_start_and_end_times(priority_schedule, table):
    local_start_times = []
    local_end_times = []
    for slot in priority_schedule.slots:
        if hasattr(slot.block, 'target'):
            local_start_times.append(utc_to_local_datetime(slot.start.iso))
            local_end_times.append(utc_to_local_datetime(slot.end.iso))
        elif slot.block:
            local_start_times.append(utc_to_local_datetime(slot.start.iso))
            local_end_times.append(utc_to_local_datetime(slot.end.iso))

    table.add_column(local_start_times, name='start time (local)', index=2)
    table.add_column(local_end_times, name="end time (local)", index=4)
    return table


def utc_to_local_datetime(utc_datetime_str):
    time_format = '%Y-%m-%d %H:%M:%S.%f'
    utc_datetime = datetime.strptime(utc_datetime_str, time_format)
    utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    local_datetime = utc_datetime.astimezone().strftime(time_format)
    return local_datetime


def make_schedule(telescope, date=None):
    if date is None:
        date = get_today()  # Current UTC date 
    date = str(date)

    target_directory_filepath = f"{os.path.join(package_directory, 'targets', date, '')}*.json"
    # Glob order is system dependent, so we will sort here to ensure consistency
    target_filepaths = sorted(glob(target_directory_filepath))
    blocks = []

    for target_filepath in target_filepaths:
        with open(target_filepath, 'r') as file:
            target_json = json.load(file)
        for target in target_json:
            if telescope.lower() == 'moa':
                blocks.append(make_block(target, readout=80))
            elif telescope.lower() == 'bc':
                blocks.append(make_block(target, readout=5))

    observatory = Observer.at_site(site_name='MJO')
    global_constraints = [AirmassConstraint(max=2.5, boolean_constraint=False),
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

    dat = '{y}-{m}-{d}'.format(y=date[0:4], m=date[4:6], d=date[6:8])
    noon_before = Time(dat + ' 06:00')
    noon_after = Time(
        dat + ' 20:00')  # start and end of night in UTC, for current UTC date

    # unused code:
    # seq_scheduler = SequentialScheduler(constraints = global_constraints,
    #                                 observer = observatory,
    #                                 transitioner = transitioner)
    # # Initialize a Schedule object, to contain the new schedule
    # sequential_schedule = Schedule(noon_before, noon_after)

    # # Call the schedule with the observing blocks and schedule to schedule the blocks
    # seq_scheduler(blocks, sequential_schedule)

    prior_scheduler = PriorityScheduler(constraints=global_constraints,
                                        observer=observatory,
                                        transitioner=transitioner)
    # Initialize a Schedule object, to contain the new schedule
    priority_schedule = Schedule(noon_before, noon_after)

    # Call the schedule with the observing blocks and schedule to schedule the blocks
    # print(blocks)
    prior_scheduler(blocks, priority_schedule)

    table = priority_schedule.to_table()
    table = add_exposure_details_to_table(priority_schedule, table)
    table = add_local_start_and_end_times(priority_schedule, table)

    save_path = package_directory + 'obs_lists/' + date + '/'
    make_dir(save_path)

    table = table.to_pandas()
    table.to_csv(save_path + 'schedule.csv', index=False)

    make_alt_plot(priority_schedule, save_path)


if __name__ == '__main__':
    date = None
    Tele = ['moa', 'bc']
    # T = 'moa'
    # for T in Tele:
    make_schedule(date, telescope='moa')
