from look_targets import make_look_list
from debass_targets import make_debass_list
from swope_targets import make_swope_list
from scheduler import make_schedule
import os


if __name__ == '__main__':
    print('!!! pulling from Git !!!')
    os.system('git pull')
    make_look_list(name_priority=[['81P',1],['73P',1],['UN271',1]],mag_priority=[['22-19',3],['19-17',4],['17-15',5],['15-12',6]])
    make_debass_list()
    make_swope_list()
    make_schedule()
    
    print('!!! pushing to Git !!!')
    os.system('git add *')
    os.system('git commit -m "update"')
    os.system('git push')