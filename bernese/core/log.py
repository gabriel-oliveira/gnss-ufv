from bernese.settings import BASE_DIR
from os import path
from datetime import datetime

def log(msg):

    now = datetime.now()
    now_tm = now.timetuple()
    filename = 'log{}{}.txt'.format(now_tm.tm_year,now_tm.tm_yday)
    logfile = path.join(BASE_DIR,'LOG',filename)
    time_msg =  now.isoformat(' ','seconds') + ': '

    with open(logfile,'a') as f:
        f.write('Em '+ time_msg + msg + '\n')
