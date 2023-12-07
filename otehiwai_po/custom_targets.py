import os
from utilly import save_targs, get_today, make_dir, make_obs_entry
from astroquery.mpc import MPC

package_directory = os.path.dirname(os.path.abspath(__file__))

def make_custom_entries(targets):
    """This largely copies make_look_entries. COme back and add bells and 
    whistles after fixing them in look and swope"""
    obs = []
    for targ in targets:
        eph = MPC.get_ephemeris(targ['name'], location='474', number=1)
        # add bells and whistles here
        ob = make_obs_entry(exptime=targ['exptime'],
                            filt=targ['filter'],
                            repeats=targ['repeats'],
                            obj=targ['name'],
                            ra=eph['RA'][0],
                            dec=eph['Dec'][0],
                            propid='',
                            magnitude=eph['V'],
                            priority=1,
                            exptype='object')
        obs += [ob]
    return obs    

def make_custom_list(targets):
    """Input targets as list of dictionaries containing:
    name recognised by MPC,
    filter to observe in
    exposure time
    and repeats.
    Uses astroquery to get current ra,dec and makes json from this.
    
    to add: Exposure calculation based on mag? see look and swope scripts
    
    Nota bene:
    Current system of getting ra,dec of object at time of executing script isn't
    great, as observation could be carried out 12 hours later and comets move.
    This is the same as the system to get the LOOK targets so is probably fine,
    but potential for error in both of these should be kept in mind.
    In short, don't trust the ra,dec given for a NEO.
    """
    date = get_today()

    save_path = os.path.join(package_directory,'targets',date)

    make_dir(save_path)
    
    custom_entries = make_custom_entries(targets)

    save_targs(custom_entries,save_path + '/custom.json')
    print('Made custom target list for ' + date + '.')


if __name__ == '__main__':
    make_custom_list()
