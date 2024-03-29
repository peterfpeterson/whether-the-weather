#!/usr/bin/env python
import numpy as np
import pandas as pd

# load the data
if 'dataframe' not in globals():
    print('loading TYS.h5')
    dataframe = pd.read_hdf('TYS.h5', 'everything')
    print('total rows', len(dataframe))

# delete the columns we aren't using
dataframe = dataframe.drop(['wind_angle'], 1)#, 'precip2', 'precip3', 'precip4'], 1) # 1=column
# set nan to zero
dataframe.precip1 = dataframe.precip1.fillna(0.)
dataframe.snow = dataframe.snow.fillna(0.)
dataframe.water_equiv = dataframe.water_equiv.fillna(0.)
# set the index
dataframe = dataframe.set_index('datetime')
print('before rain1', dataframe['precip1'].fillna(0.).sum())
print('before rain2', dataframe['precip2'].fillna(0.).sum())
print('before rain3', dataframe['precip3'].fillna(0.).sum())
print('before rain4', dataframe['precip4'].fillna(0.).sum())
print('before snow', dataframe['snow'].fillna(0.).sum())
print('before depth', dataframe['water_equiv'].fillna(0.).sum())

#cols = ('datetime', 'wind_speed' - avg, 'temperature' - min/max, 'dewpoint' min/max,
#        'pressure' avg, 'precip1' sum, 'snow' sum, 'water_equiv' sum)

df_mean = dataframe[['wind_speed', 'pressure']].dropna().resample('D').mean()
df_sum  = dataframe[['precip1', 'precip2', 'precip3', 'precip4', 'snow', 'water_equiv']].fillna(0.).resample('D').sum()
df_min  = dataframe[['temperature', 'dewpoint']].resample('D').min().rename(columns={'temperature':'temp_min',
                                                                       'dewpoint':'dew_min'})
df_max  = dataframe[['temperature', 'dewpoint']].resample('D').max().rename(columns={'temperature':'temp_max',
                                                                       'dewpoint':'dew_max'})
dataframe = pd.concat([df_mean, df_sum, df_min, df_max], axis=1)
del df_mean
del df_sum
del df_min
del df_max
print('after rain ', dataframe['precip1'].fillna(0.).sum())
print('after snow ', dataframe['snow'].fillna(0.).sum())
willrain = dataframe.precip1.values > 0. 
willsnow = dataframe.snow.values > 0. 
pressure_change = dataframe.pressure.values[1:]-dataframe.pressure.values[:-1]
dataframe = dataframe.drop(dataframe.index[-1])
dataframe['willrain'] = willrain[1:]
dataframe['willsnow'] = willsnow[1:]
dataframe['press_change'] = pressure_change

dataframe.to_hdf('TYS_daily.h5', 'everything', format='table')
