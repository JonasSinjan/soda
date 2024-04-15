from datetime import datetime, date
import pathlib
import pandas as pd

import requests
from sunpy import time
import urllib.parse

_MISSION_BEGIN = time.parse_time(datetime(2020, 1, 1))
_NOW = time.parse_time(datetime.now())
_CACHE_DIR = (pathlib.Path(__file__) / '..' / '.data').resolve()
_CACHE_DIR.mkdir(exist_ok=True)


class DataProduct:
    def __init__(self, descriptor, low_latency=False):
        """
        Parameters
        ----------
        descriptor: str
            Data product descriptor. These can be found by searching for data
            on http://soar.esac.esa.int/soar/#search, and identifying the
            descriptor from the "Descriptor" column.
        low_latency: bool, optional
            If `True`, query low latency data instead of science data.
        """
        self.descriptor = descriptor
        self.low_latency = low_latency

    @property
    def latest_path(self):
        """
        Path to data updated today.
        """
        datestr = _NOW.strftime('%Y-%m-%d')
        return _CACHE_DIR / f'{self.descriptor}_{datestr}.csv'

    @property
    def intervals(self):
        """
        All available intervals for this data product.
        """
        if not self.latest_path.exists():
            self.save_remote_intervals()

        df = pd.read_csv(self.latest_path,
                         parse_dates=['Start', 'End'])
        return df

    def save_remote_intervals(self):
        """
        Get and save the intervals of all data files available in the
        Solar Oribter Archive for a given data descriptor.
        """
        print(f'Updating intervals for {self.descriptor}...')
        src_str =  ('http://soar.esac.esa.int/soar-sl-tap/tap')
        begin_time = _MISSION_BEGIN.isot.replace('T', '+').split('.')[0]
        end_time = _NOW.isot.replace('T', '+').split('.')[0]
        print(begin_time, end_time)
        
        extra_url_elements = "/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=JSON&QUERY="

        ADQL = f"SELECT+*+FROM+v_sc_data_item+WHERE+descriptor='{self.descriptor}'"

        url = src_str + extra_url_elements + ADQL#urllib.parse.quote(ADQL)
        print(url)

        # Get request info
        r = requests.get(url)
        # TODO: intelligently detect and error on a bad descriptor
        # with open('./test.csv', 'w+b') as file:
        #     response = requests.get(url) # get request
        #     file.write(response.content)
        # df = pd.read_csv('./test.csv')
        # Do some list/dict wrangling
        #print(r.json())
        names = [m['name'] for m in r.json()['metadata']]
        #print(r.json())
        info = {name: [] for name in names}
        for entry in r.json()['data']:
            for i, name in enumerate(names):
                info[name].append(entry[i])

        # Setup intervals
        intervals = []
        for start, end in zip(info['begin_time'], info['end_time']):
            intervals.append([time.parse_time(start).datetime,
                              time.parse_time(end).datetime])

        df = pd.DataFrame(intervals)
        df.columns = ['Start', 'End']
        df.to_csv(self.latest_path, index=False)
