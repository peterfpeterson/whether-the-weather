#!/usr/bin/env python
import os
import requests
import sys
from urllib.request import urlopen
from urllib.error import URLError

# document describing format ftp://ftp.ncdc.noaa.gov/pub/data/noaa/ish-format-document.pdf
FILE_TEMPLATE = '{USAF:05d}-{WBAN:05d}-{year}.gz'
URL_TEMPLATE = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/{year}/'
data_dir = os.path.expanduser('~/tmp')

# station list at ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv
STATION = 'GHCND:USW00013891' #'KTYS' valid for 1948 through 2017
USAF=723260
WBAN=13891

for year in range(1948,2018):
    filename = FILE_TEMPLATE.format(USAF=USAF, WBAN=WBAN, year=year)
    target_file = os.path.join(data_dir, filename)
    # keep going if the file exists
    if os.path.exists(target_file):
        print(filename, 'exists')
    else:
        url = URL_TEMPLATE.format(USAF=USAF, WBAN=WBAN, year=year) + filename
        print('downloading', url, 'to', data_dir)
        try:
            with open(target_file, 'wb') as fout:
                print(url)
                fout.write(urlopen(url).read())
        except URLError as e:
            print('failed to download', filename)
            print(e)
            if os.path.exists(target_file):
                os.unlink(target_file)
