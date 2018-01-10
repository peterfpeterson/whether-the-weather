#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans

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
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('precip4')] # celsius
    rain[i] = data.values[:365]

    # snow
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('water_equiv')] # celsius
    snow[i] = data.values[:365]

'''
##### minimum temperature
fig, ax = plt.subplots()
ax.set_title('daily minimum temperature')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(temp_min),
                  vmin=-10,#np.nanmin(temp_min),
                  vmax=40)#np.nanmax(temp_min))
fig.colorbar(c)
fig.show()

##### maximum temperature
fig, ax = plt.subplots()
ax.set_title('daily maximum temperature')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(temp_max),
                  vmin=-10,#np.nanmin(temp_max),
                  vmax=40)#np.nanmax(temp_max))
fig.colorbar(c)
fig.show()
'''

##### rain
fig, ax = plt.subplots()
ax.set_title('rain')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(rain),
                  vmin=0.,
                  vmax=10.)#np.nanmax(rain))
fig.colorbar(c)
fig.show()

'''
##### snow
fig, ax = plt.subplots()
ax.set_title('snow')
c = ax.pcolormesh(dayofyear, years, np.ma.masked_invalid(snow),
                  vmin=0.,
                  vmax=100.,#np.nanmax(snow))
                  norm=PowerNorm(gamma=1./2.))#LogNorm())
fig.colorbar(c)
fig.show()
'''
