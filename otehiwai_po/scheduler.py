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

from utils import *
import os
package_directory = os.path.dirname(os.path.abspath(__file__)) + '/'

def make_target(ra,dec,name):
    c = SkyCoord(ra,dec,unit=u.deg)
    targ = FixedTarget(coord=c,name=name)
    return targ

def make_block(obj,priority=0,readout=80):

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

def make_alt_plot(priority_schedule,save_path):
    import warnings
    warnings.filterwarnings("ignore")

    from astroplan.plots import plot_schedule_airmass
    import matplotlib.pyplot as plt

    # plot the schedule with the airmass of the targets
    plt.figure(figsize = (14,6))
    plot_schedule_airmass(priority_schedule,show_night='True',use_local_tz=True)
    plt.legend(loc = "upper right")
    plt.savefig(save_path+'alt_plot.pdf')


def make_schedule(date=None,telescope='moa'):
    if date is None:
        date = get_today()
    date = str(date)
    
    print(package_directory + date)
    targets = glob(package_directory + 'targets/' + date + '/*.json' )
    blocks = []
    print(targets)
    for target in targets:
        print('!!!! ',target)
        targ = json.load(open(target))
        for ob in targ:
            blocks +=  [make_block(ob)]
    
    observatory = Observer.at_site(site_name='MJO')
    global_constraints = [AirmassConstraint(max = 2.5, boolean_constraint = False),
                      AtNightConstraint.twilight_civil()]
    if telescope.lower() == 'moa':
        transitioner = MOA_transitioner()
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
    prior_scheduler(blocks, priority_schedule)

    table = priority_schedule.to_table()

    save_path = package_directory + 'obs_lists/' + date + '/'
    make_dir(save_path)

    table = table.to_pandas()

    schedule = block_schedule(table,date=date)


    schedule.to_csv(save_path + 'schedule.csv',index=False)

    make_alt_plot(priority_schedule,save_path)

def split_coords(ra,dec):
    hr = ra.split('h')[0]
    hmin = ra.split('h')[-1].split('m')[0]
    hsec = int(float(ra.split('m')[-1].split('s')[0]))

    deg = dec.split('d')[0]
    dmin = dec.split('d')[-1].split('m')[0]
    dsec = int(float(dec.split('m')[-1].split('s')[0]))

    return hr, hmin, hsec, deg, dmin, dsec

def block_schedule(schedule,date=None):
    if date is None:
        date = get_today()
    date = str(date)
    save_path = package_directory + 'blocks/' + date + '/'
    make_dir(save_path)

    t = []
    for i in range(len(schedule)):
        t += [Time(schedule['start time (UTC)'].values[i]).jd]

    start = 0
    blocks = []
    schedule['block'] = 0
    b = 1
    while start < len(t):
        tt = t - t[start]
        tt[tt<=0] = 1e6
        ind = np.argmin(abs(tt - 1.05/24))
        if len(schedule.iloc[ind:]) < 2:
            ind = len(schedule)
        blocks += [schedule.iloc[start:ind].reset_index()]
        schedule['block'].iloc[start:ind] = b

        start = ind
        b += 1
        
    for bind in range(len(blocks)):
        b = blocks[bind]
        b = b.drop(np.where(b.target.values == 'TransitionBlock')[0])

        un2 = 0; un3 = 0
        automate = ''
        for i in range(len(b)):
            entry = b.iloc[i]
            name = entry.target
            name = name.replace(' ','')
            #if len(name) > 16:
            #    n1, n2 = name.split('_22S')
            #    name = n1[:len(name) - 6] + '_22S' + n2
            #    print('!!! renaming{} to {}'.format(entry.target,name))
            exptime = int(entry['exptime (s)'])
            filt = entry['configuration']['filter']
            hr, hmin, hsec, deg, dmin, dsec = split_coords(entry.ra,entry.dec)
            repeats = entry.repeats
            line = f'{name} {exptime} {filt} {hr:0>2} {hmin:0>2} {hsec:0>2} {deg[0]}{deg[1:]:0>2} {dmin:0>2} {dsec:0>2} 2000.0 {repeats} {un2} {un3}\n'
            automate += line
        automate = automate[:-1]
        with open(f'{save_path}UC_block_{bind+1}.lst', 'w') as f:
            f.write(automate)
    
    return schedule



if __name__ == '__main__':
    make_schedule()