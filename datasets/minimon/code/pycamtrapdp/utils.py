import os
import uuid_utils
from datetime import datetime, timedelta
from xmlrpc.client import DateTime
import pandas as pd
import numpy as np
from datetime import datetime

def generate_id(length=8):
    return os.urandom(length).hex()

def generate_uuid():
    return uuid_utils.uuid7().hex

def parse_filename(filename):
        basename, extension = os.path.splitext(filename)
        nameparts = basename.split('_')

        filenamedict = {
                        'cam_id': nameparts[0],
                        'datetime': nameparts[1],
                        'burst': None,
                        'ms': None,
                        'ext': extension,
                        'filename': filename
        }

        filenamedict['datetime_iso'] = str_time_to_ISO(filenamedict['datetime'])  # convert datestring to ISO time
        if extension == '.jpg':
            filenamedict['burst'] = nameparts[2]
            filenamedict['ms'] = nameparts[3]

        return filenamedict


def str_time_to_ISO(strtime, format="%Y%m%d%H%M%S"):
    dt = datetime.strptime(f"{strtime}", format)
    return  dt.isoformat(timespec='seconds')


def datetime_from_ISO(isostr):
    dt = datetime.fromisoformat(isostr)
    return dt

def obj_to_csv(obj_list, csvpath, overwrite=False):
    # df = pd.DataFrame.from_dict(objlist)

    df = pd.DataFrame([o.as_dict() for o in obj_list])
    # if os.path.exists(csvpath) and not overwrite:
    #     old_df = pd.read_csv(csvpath)
    #     df = pd.concat([old_df, df], axis=0, ignore_index=True)
    if not os.path.exists(csvpath) or overwrite:
        mode = 'w'
    else:
        mode = 'a'

    df.to_csv(csvpath, index=False, mode=mode, header=(mode == 'w'))



