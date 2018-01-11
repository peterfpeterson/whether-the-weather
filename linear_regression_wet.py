#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import linear_model

# load the data
if 'dataframe' not in globals():
    print('loading TYS.h5')
    dataframe = pd.read_hdf('TYS.h5', 'everything')
    print('total rows', len(dataframe))

# delete the columns we aren't using
for name in ['wind_angle', 'wind_speed', 'pressure', 'dewpoint', 'temperature']:
    dataframe = dataframe.drop(name, 1) # 1=column
#dataframe = dataframe.dropna().set_index('datetime') # drop nan temperatures
dataframe = dataframe.fillna(0.).set_index('datetime') # drop nan temperatures
dataframe = dataframe[dataframe.index > np.datetime64('2017-01-01T00:00:00')]
dataframe['dayofyear'] = dataframe.index.dayofyear
dataframe = dataframe.set_index('dayofyear')
dataframe = dataframe.sort_index()
dataframe = dataframe.groupby(dataframe.index).sum()
dataframe.precip1 *= 24*.1
dataframe.snow *= 24*.1

############################## daily minimum
def getNext(fullX, fullY, dayfromend):
    linear = linear_model.LinearRegression()
    low,high = dayfromend-3, fullX.size+dayfromend
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
x,rain,snow = (np.arange(366-32, 366), np.zeros(32), np.zeros(32))
for i in range(31):
    #print(i, x[i])
    rain[i] = getNext(dataframe.index, dataframe.precip1, x[i]-365)
    snow[i] = getNext(dataframe.index, dataframe.snow, x[i]-365)
#print(x.size, rain.size, snow.size)

# create figure
fig, ax = plt.subplots()
ax.set_title('linear regression - 3 day window')
ax.plot(x, rain, label='rain pred')
#ax.plot(x, snow, label='snow pred')
'''
# plot daily min and max
#ax.fill_between(x, low, high, color='grey')
#ax.fill_between(minmaxtemp.index.values, minmaxtemp.temp_min, minmaxtemp.temp_max, color='grey')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_min, color='grey')
#ax.plot(minmaxtemp.index.values, minmaxtemp.temp_max, color='grey')
'''

ax.plot(dataframe.index.values, dataframe.precip1, label='precip1')
#ax.plot(dataframe.index.values, dataframe.precip2, label='precip2')
#ax.plot(dataframe.index.values, dataframe.precip3, label='precip3')
#ax.plot(dataframe.index.values, dataframe.precip4, label='precip4')
#ax.plot(dataframe.index.values, dataframe.snow, label='snow')
#ax.plot(dataframe.index.values, dataframe.water_equiv, label='water')
ax.legend()
'''
# plot hourly actuals
for year in [2017]:
    startdate = np.datetime64('{}-01-01T00:00'.format(year))
    enddate = np.datetime64('{}-12-31T23:59'.format(year))
    #mask = (dataframe.index >= startdate) & (dataframe.index <= enddate)
    data = dataframe.loc[(dataframe.index >=startdate) & (dataframe.index<=enddate), ('temperature')] # celsius
    alpha = .2
    if year == 2017:
        alpha = 1.
    ax.plot((data.index.values - startdate) / np.timedelta64(1,'D'), data, label=str(year), alpha=alpha)
'''

# add lines for month boundaries
daynum = 0
for number in [0,31,28,31,30,31,30,31,31,30,31,30,31,0]:
    ax.plot((daynum,daynum), (-1,18), color='k')
    daynum += number

ax.set_xlim(335,364.5)
ax.set_ylim(-1,18)
fig.show()
