#!/usr/bin/env python
import datetime
import gzip
import numpy as np
import os
import pandas as pd
import requests
import sys
from urllib.request import urlopen
from urllib.error import URLError


# document describing format ftp://ftp.ncdc.noaa.gov/pub/data/noaa/ish-format-document.pdf
FILE_TEMPLATE = '{USAF:05d}-{WBAN:05d}-{year}.gz'
URL_TEMPLATE = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/{year}/'
data_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]

# station list at ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv
STATION = 'GHCND:USW00013891' #'KTYS' valid for 1948 through 2017
USAF=723260
WBAN=13891
# years that don't exist for this station
BAD_YEAR = [1965,1966,1967,1968,1969,1970,1971,1972]

########## download gz version of everything
filenames = []
for year in range(1948,2019):
    if year in BAD_YEAR:
        print('skipping', year)
        continue

    filename = FILE_TEMPLATE.format(USAF=USAF, WBAN=WBAN, year=year)
    filenames.append(os.path.join(data_dir, filename))
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

########## extract the data into a panda DataFrame
def convertvalue(value, scale, missing_value):
    try:
        if int(value) == missing_value:
            return np.nan
        else:
            return float(value) / scale
    except ValueError:
        return np.nan

def extract_date_time(row):
    '''
    POS: 16-23 GEOPHYSICAL-POINT-OBSERVATION date
    POS: 24-27 GEOPHYSICAL-POINT-OBSERVATION time
               The time of a GEOPHYSICAL-POINT-OBSERVATION based on
               Coordinated Universal Time Code (UTC).
    '''
    fmt_str = '%Y%m%d%H%M'
    dt = datetime.datetime.strptime(row[15:27], fmt_str)
    return (dt,)# dt.year, dt.month, dt.day, dt.hour

def extract_wind(row):
    '''
    POS: 61-63 WIND-OBSERVATION direction angle
      The angle, measured in a clockwise direction, between true north and the direction from which
      the wind is blowing.
      MIN: 001 MAX: 360 UNITS: Angular Degrees
      SCALING FACTOR: 1
      DOM: A general domain comprised of the numeric characters (0-9).
      999 = Missing. If type code (below) = V, then 999 indicates variable wind direction.
    POS: 65-65 WIND-OBSERVATION type code
      The code that denotes the character of the WIND-OBSERVATION.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      A: Abridged Beaufort
      B: Beaufort
      C: Calm
      H: 5-Minute Average Speed
      N: Normal
      R: 60-Minute Average Speed
      Q: Squall
      T: 180 Minute Average Speed
      V: Variable
      9 = Missing
      NOTE: If a value of 9 appears with a wind speed of 0000, this indicates calm winds.
    POS: 66-69 WIND-OBSERVATION speed rate
      The rate of horizontal travel of air past a fixed point.
      MIN: 0000 MAX: 0900 UNITS:
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9).
      9999 = Missing.
    '''
    angle = convertvalue(int(row[60:63]), 1., 999)
    speed = convertvalue(int(row[65:69]), 10., 9999)
    return angle, speed

def extract_temperature(row):
    '''
    POS: 88-92 AIR-TEMPERATURE-OBSERVATION air temperature
      The temperature of the air.
      MIN: -0932 MAX: +0618 UNITS: Degrees Celsius
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9), a plus sign (+), and a minus
      sign (-).
      +9999 = Missing.
    POS: 94-98 AIR-TEMPERATURE-OBSERVATION dew point temperature
      The temperature to which a given parcel of air must be cooled at constant pressure and water vapor
      content in order for saturation to occur.
      MIN: -0982 MAX: +0368 UNITS: Degrees Celsius
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9), a plus
      sign (+), and a minus sign (-).
      +9999 = Missing.
    '''
    temp = convertvalue(int(row[87:92]), 10., 9999)
    dew = convertvalue(int(row[93:98]), 10., 9999)

    return temp, dew

def extract_pressure(row):
    '''
    POS: 100-104 ATMOSPHERIC-PRESSURE-OBSERVATION sea level pressure
      The air pressure relative to Mean Sea Level (MSL).
      MIN: 08600 MAX: 10900 UNITS: Hectopascals
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9).
      99999 = Missing.
    '''
    return (convertvalue(int(row[99:104]), 10., 99999), )

def extract_precipitation(row):
    '''
    FLD LEN: 3 LIQUID-PRECIPITATION occurrence identifier
      The identifier that represents an episode of LIQUID-PRECIPITATION.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      AA1 - AA4 An indicator of up to 4 repeating fields of the following items:
      LIQUID-PRECIPITATION period quantity
      LIQUID-PRECIPITATION depth dimension
      LIQUID-PRECIPITATION condition code
      LIQUID-PRECIPITATION quality code
    FLD LEN: 2 LIQUID-PRECIPITATION period quantity in hours
      The quantity of time over which the LIQUID-PRECIPITATION was measured.
      MIN: 00 MAX: 98 UNITS: Hours
      SCALING FACTOR: 1
      DOM: A specific domain comprised of the characters in the ASCII character set
      99 = Missing.
    FLD LEN: 4 LIQUID-PRECIPITATION depth dimension
      The depth of LIQUID-PRECIPITATION that is measured at the time of an observation.
      MIN: 0000 MAX: 9998 UNITS: millimeters
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9).
      9999 = Missing.
    FLD LEN: 1 LIQUID-PRECIPITATION condition code
      The code that denotes whether a LIQUID-PRECIPITATION depth dimension was a trace value.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      1: Measurement impossible or inaccurate
      2: Trace
      3: Begin accumulated period (precipitation amount missing until end of accumulated period)
      4: End accumulated period
      5: Begin deleted period (precipitation amount missing due to data problem)
      6: End deleted period
      7: Begin missing period
      8: End missing period
      E: Estimated data value (eg, from nearby station)
      I: Incomplete precipitation amount, excludes one or more missing reports, such as one or more 15-minute
      reports not included in the 1-hour precipitation total
      J: Incomplete precipitation amount, excludes one or more erroneous reports, such as one or more 1-hour
      precipitation amounts excluded from the 24-hour total
      9: Missing
    '''
    def convertValue(stuff=''):
        if len(stuff) == 0:
            return 0. # 0 hours, 0 cm
        else:
            hours = convertvalue(stuff[:2], 1, 99)
            millis = convertvalue(stuff[2:8], 10, 9999)
            #return (int(stuff[:2]), int(stuff[2:8])) # hours, cm
            rate = millis * .1 / hours
            if np.isnan(rate):
                return 0.
            #print(millis, hours, rate)
            return millis / hours

    if 'AA' not in row:
        return (convertValue(),) # 0 hours, 0 cm

    values = []
    for key in ['AA1', 'AA2', 'AA3', 'AA4']:
        if key in row:
            index = row.index(key)
            value = row[index+3:index+10]
            row = row[index+9:]
            #print('>>>', value)
            if value[-1] in '2': #not in '19':
                values.append(convertValue(value))
            else:
                values.append(0.)
        else:
            values.append(0.)
    #print('---', values)
    return tuple(values)

def extract_precipitation2(row):
    '''
    FLD LEN: 3 15 Minute LIQUID-PRECIPITATION occurrence identifier
      The identifier that represents an episode of LIQUID-PRECIPITATION.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      IMPORTANT NOTE: These data are also provided in the AAx section for typical use in applications. The APx data are mainly
      intended for quality control processing.
      AP1 Indicates HPD gauge value 45 minutes prior to observation time
      AP2 Indicates HPD gauge value 30 minutes prior to observation time
      AP3 Indicates HPD gauge value 15 minutes prior to observation time
      AP4 Indicates HPD gauge value at observation time
      LIQUID-PRECIPITATION depth dimension
      LIQUID-PRECIPITATION condition code
      LIQUID-PRECIPITATION quality code
    FLD LEN: 4 HPD (Hourly Precipitation Data network) gauge value
      The HPD Gauge value that is measured at the time indicated.
      MIN: 0000 MAX: 9998 UNITS: millimeters
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9).
      9999 = Missing
    '''
    # didn't appear in 2017 data
    pass

def extract_snow(row):
    '''
    FLD LEN: 3 SNOW-DEPTH identifier
      The identifier that denotes the start of a SNOW-DEPTH data section.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      AJ1 An indicator of the occurrence of the following items:
      SNOW-DEPTH dimension
      SNOW-DEPTH condition code
      SNOW-DEPTH quality code
      SNOW-DEPTH equivalent water depth dimension
      SNOW-DEPTH equivalent water condition code
      SNOW-DEPTH equivalent water condition quality code
    FLD LEN: 4 SNOW-DEPTH dimension
      The depth of snow and ice on the ground.
      MIN: 0000 MAX: 1200 UNITS: centimeters
      SCALING FACTOR: 1
      DOM: A general domain comprised of the numeric characters (0-9).
      9999 = Missing.
    FLD LEN: 1 SNOW-DEPTH condition code
      The code that denotes specific conditions associated with the measurement of snow in a
      PRECIPITATION-OBSERVATION.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      1: Measurement impossible or inaccurate
      2: Snow cover not continuous
      3: Trace
      4: End accumulated period (data include more than one day)
      5: End deleted period (data eliminated due to quality problems)
      6: End missing period
      E: Estimated data value (eg, from nearby station)
      9: Missing
    FLD LEN: 6 SNOW-DEPTH equivalent water depth dimension
      The depth of the liquid content of solid precipitation that has accumulated on the ground.
      MIN: 000000 MAX: 120000 UNITS: millimeters
      SCALING FACTOR: 10
      DOM: A general domain comprised of the numeric characters (0-9).
      999999 = Missing.
    FLD LEN: 1
      SNOW-DEPTH equivalent water condition code
      The code that denotes specific conditions associated with the measurement of the SNOW-DEPTH.
      DOM: A specific domain comprised of the characters in the ASCII character set.
      1: Measurement impossible or inaccurate
      2: Trace
      9: Missing (no special code to report)
    '''
    snow_depth = np.nan
    water_depth = np.nan
    if 'AJ1' in row:
        index = row.index('AJ1')
        everything = row[index+3:index+15]
        snow_depth, snow_cond = everything[0:5], everything[5:6]
        water_depth, water_cond = everything[6:11], everything[11:]
        
        if snow_cond in '1239':
            snow_depth = np.nan
        else:
            snow_depth = convertvalue(snow_depth, 1, 9999)
            if snow_depth > float(1200):
                snow_depth = np.nan

        if water_cond in '1239':
            water_depth = np.nan
        else:
            water_depth = convertvalue(water_depth, 10, 999999)
            if water_depth > float(120000):
                water_depth = np.nan
    return snow_depth*10, water_depth

def ingest_file(fname):
    print('***', fname)
    with gzip.open(fname, 'rt', encoding='ascii') as f:
        data = [extract_date_time(ln) + extract_wind(ln) + extract_temperature(ln)
                + extract_pressure(ln) + extract_precipitation(ln) + extract_snow(ln)
                for ln in f]
    #with gzip.open(fname, 'rt', encoding='ascii') as f:
    #    [print(extract_precipitation(ln)) for ln in f]

    cols = ('datetime', #'year', 'month', 'day', 'hour',
            'wind_angle', 'wind_speed',
            'temperature', 'dewpoint','pressure',
            'precip1', 'precip2', 'precip3', 'precip4',
            'snow', 'water_equiv')
    return pd.DataFrame(data, columns=cols)#.dropna()

# get rid of files that have issues
print('number of files', len(filenames))
filenames = [filename for filename in filenames
             if ('1973.gz' not in filename) and ('1975.gz' not in filename)]
print('number of files', len(filenames))

#alldata = ingest_file('723260-13891-2017.gz')
#print(alldata.precip1.values[-24*4:])
# ingest everything and put it into a single file
alldata = [ingest_file(filename) for filename in filenames]
everything = pd.concat(alldata)
del alldata

# write out to file
print('orig ', len(everything))
everything.to_hdf('TYS.h5', 'everything', format='table')

# how to load the data
#other = pd.read_hdf('TYS.h5', 'everything')
#print('other', len(other))
