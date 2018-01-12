#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from month_marks import month_ticks, month_label

# load the data
print('loading TYS_daily.h5')
dataframe = pd.read_hdf('TYS_daily.h5', 'everything')
print('total rows', len(dataframe))

years = np.arange(1948,2018, dtype=np.float)
dayofyear = np.arange(0,365, dtype=np.float)
temp_min = np.full([years.size,dayofyear.size], np.nan)
temp_max = np.full([years.size,dayofyear.size], np.nan)
rain = np.full([years.size,dayofyear.size], np.nan)
snow = np.full([years.size,dayofyear.size], np.nan)

for i, year in enumerate(range(1948, 2018)):
    startdate = np.datetime64('{}-01-01'.format(year))
    enddate = np.datetime64('{}-12-31'.format(year))
    # minimum temperature
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('temp_min')] # celsius
    temp_min[i] = data.values[:365]

    # maximum temperature
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('temp_max')] # celsius
    temp_max[i] = data.values[:365]

    # rain
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('precip1')] # celsius
    rain[i] = data.values[:365]

    # snow
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('snow')] # celsius
    snow[i] = data.values[:365]

years = years[-41:]

##### minimum temperature
temp_min = temp_min[-41:,:]
fig, ax = plt.subplots()
ax.set_title('daily minimum temperature in C')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(temp_min),
                  label='stuff',
                  cmap='viridis',
                  vmin=-10,#np.nanmin(temp_min),
                  vmax=40)#np.nanmax(temp_min))
ax.set_yticks(np.arange(1980,2020,5))
ax.set_ylabel('year')
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_label)
c = fig.colorbar(c)
c.set_label('Celsius')
fig.show()

##### maximum temperature
temp_max = temp_max[-41:,:]
fig, ax = plt.subplots()
ax.set_title('daily maximum temperature in C')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(temp_max),
                  cmap='viridis',
                  vmin=-10,#np.nanmin(temp_max),
                  vmax=40)#np.nanmax(temp_max))
ax.set_yticks(np.arange(1980,2020,5))
ax.set_ylabel('year')
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_label)
c = fig.colorbar(c)
c.set_label('Celsius')
fig.show()

##### rain
rain = rain[-41:,:]
fig, ax = plt.subplots()
ax.set_title('rain in cm')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(rain),
                  cmap='viridis',
                  vmin=0.,
                  vmax=8.)#np.nanmax(rain))
ax.set_yticks(np.arange(1995,2020,5))
ax.set_ylim(1997, 2017)
ax.set_ylabel('year')
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_label)
c = fig.colorbar(c)
c.set_label('centimeters')
fig.show()
'''

##### snow
snow = snow[-22:,:]
fig, ax = plt.subplots()
ax.set_title('snow')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(snow),
                  vmin=0.,
                  vmax=np.nanmax(snow))
                  #norm=PowerNorm(gamma=1./2.))#LogNorm())
fig.colorbar(c)
fig.show()
'''
