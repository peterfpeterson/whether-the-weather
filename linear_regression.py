#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import linear_model
from month_marks import month_ticks, month_label, colors

# load in all the year actuals
print('loading TYS_daily.h5')
actual = pd.read_hdf('TYS_daily.h5', 'everything')
actual = actual.drop(['wind_speed', 'pressure', 'precip1', 'precip2',
                      'precip3', 'precip4', 'snow', 'water_equiv',
                      'dew_min', 'dew_max', 'willrain', 'willsnow', 'press_change'], 1) # 1=column
actual = actual[(actual.index >= np.datetime64('2017-01-01')) & 
                (actual.index <= np.datetime64('2017-12-31'))]
actual['dayofyear'] = actual.index.dayofyear
actual = actual.set_index('dayofyear')
actual = actual.sort_index()

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
dataframe = dataframe[dataframe.index > np.datetime64('2017-01-01T00:00:00')]

# create the table of mins and maxs
mintemp = dataframe.resample('D').min().rename(columns={'temperature':'temp_min'})
maxtemp = dataframe.resample('D').max().rename(columns={'temperature':'temp_max'})
minmaxtemp = pd.concat([mintemp, maxtemp], axis=1)
del mintemp
del maxtemp
minmaxtemp['dayofyear'] = minmaxtemp.index.dayofyear
minmaxtemp = minmaxtemp.set_index('dayofyear')
minmaxtemp = minmaxtemp.sort_index()
#minmaxtemp = minmaxtemp.groupby(minmaxtemp.index).mean()

############################## daily minimum
def getNext(fullX, fullY, dayfromend):
    linear = linear_model.LinearRegression()
    low,high = dayfromend-14, fullX.size+dayfromend
    #print(low,high)
    trainX = np.asarray(fullX[low:high]).reshape(-1, 1)
    trainY = np.asarray(fullY[low:high]).reshape(-1, 1)
    linear.fit(trainX, trainY)
    linear.score(trainX, trainY)
    #print('Coefficient: \n', linear.coef_)
    #print('Intercept: \n', linear.intercept_)
    #print('R² Value: \n', linear.score(trainX, trainY))
    predicted = linear.predict([[365+dayfromend]])
    return predicted.ravel()[0]
##############################
x,low,high = (np.arange(366-32, 366), np.zeros(32), np.zeros(32))
for i in range(31):
    #print(i, x[i])
    low[i] = getNext(minmaxtemp.index, minmaxtemp.temp_min, x[i]-365)
    high[i] = getNext(minmaxtemp.index, minmaxtemp.temp_max, x[i]-365)
print(x.size, low.size, high.size)

# create figure
fig, ax = plt.subplots()
ax.set_title('Linear Regression - 14 Day Window')

# plot daily min and max
ax.fill_between(x, low, high, color=colors[9])
#ax.fill_between(minmaxtemp.index.values, minmaxtemp.temp_min, minmaxtemp.temp_max, color='grey')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_min, color='grey')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_max, color='grey')

# plot hourly actuals
for year in [2017]:
    startdate = np.datetime64('{}-01-01T00:00'.format(year))
    enddate = np.datetime64('{}-12-31T23:59'.format(year))
    #mask = (dataframe.index >= startdate) & (dataframe.index <= enddate)
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('temperature')] # celsius
    alpha = .2
    if year == 2017:
        alpha = 1.
    ax.plot((data.index.values - startdate) / np.timedelta64(1,'D'), data, label=str(year), alpha=alpha,
            color=colors[2])

'''
# add lines for month boundaries
daynum = 0
for number in [0,31,28,31,30,31,30,31,31,30,31,30,31,0]:
    ax.plot((daynum,daynum), (-20,40), color='k')
    daynum += number
'''

ax.set_xticks(month_ticks)
ax.set_xticklabels(month_label)
ax.set_ylabel('temperature in C')
ax.set_xlim(304,364.5)
ax.set_ylim(-8,26)
fig.show()

print('mean abs diff in min', np.abs(low - actual.temp_min.values[-1*low.size:]).mean())
print('mean abs diff in max', np.abs(high - actual.temp_max.values[-1*high.size:]).mean())
