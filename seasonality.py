#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# load the data
if 'dataframe' not in globals():
    print('loading TYS.h5')
    dataframe = pd.read_hdf('TYS.h5', 'everything')
    print('total rows', len(dataframe))

# delete the columns we aren't using
for name in ['wind_angle', 'wind_speed', 'pressure', 'dewpoint', 'precip1',
             'precip2', 'precip3', 'precip4', 'snow', 'water_equiv']:
    dataframe = dataframe.drop(name, 1) # 1=column
dataframe = dataframe.dropna().set_index('datetime') # drop nan temperatures

# create the table of mins and maxs
mintemp = dataframe.resample('D').min().rename(columns={'temperature':'temp_min'})
maxtemp = dataframe.resample('D').max().rename(columns={'temperature':'temp_max'})
minmaxtemp = pd.concat([mintemp, maxtemp], axis=1)
del mintemp
del maxtemp
minmaxtemp['dayofyear'] = minmaxtemp.index.dayofyear
minmaxtemp = minmaxtemp.set_index('dayofyear')
minmaxtemp = minmaxtemp.sort_index()
minmaxtemp = minmaxtemp.groupby(minmaxtemp.index).mean()

# create figure
fig, ax = plt.subplots()
ax.set_title('seasonality - 12 months')

# plot daily min and max
ax.fill_between(minmaxtemp.index.values, minmaxtemp.temp_min, minmaxtemp.temp_max, color='cyan')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_min, color='grey')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_max, color='grey')

# plot hourly actuals
for year in [2017]: #range(1976, 2018):
    startdate = np.datetime64('{}-01-01T00:00'.format(year))
    enddate = np.datetime64('{}-12-31T23:59'.format(year))
    #mask = (dataframe.index >= startdate) & (dataframe.index <= enddate)
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('temperature')] # celsius
    alpha = .2
    if year == 2017:
        alpha = 1.
    ax.plot((data.index.values - startdate) / np.timedelta64(1,'D'), data, label=str(year),
            alpha=alpha, color='darkblue')

# add lines for month boundaries
daynum = 0
for number in [0,31,28,31,30,31,30,31,31,30,31,30,31,0]:
    ax.plot((daynum,daynum), (-20,40), color='k')
    daynum += number

fig.show()
