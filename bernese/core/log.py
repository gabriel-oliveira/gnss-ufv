from bernese.settings import BASE_DIR
from os import path
from datetime import datetime

def log(msg):

    logfile = path.join(BASE_DIR,'LOG.TXT')
    time_msg =  datetime.now().isoformat(' ','seconds') + ': '

    with open(logfile,'a') as f:
        f.write('Em '+ time_msg + msg + '\n')
