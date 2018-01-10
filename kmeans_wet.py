#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans

# load the data
print('loading TYS_daily.h5')
dataframe = pd.read_hdf('TYS_daily.h5', 'everything').dropna()
print('total rows', len(dataframe))

# split into train and test
training = dataframe[dataframe.index < np.datetime64('2017-12-01')]
test = dataframe[dataframe.index >= np.datetime64('2017-12-01')]

labels_class = [#'wind_speed',
                #'temp_min',
                #'temp_max',
                #'dew_min',
                #'dew_max',
                #'pressure',
                'press_change',
                'precip1',
                #'snow',
                #'water_equiv'
                ]

# run it
decision = KMeans(n_clusters=2)
decision.fit(training[labels_class],
             training[['willrain']])#,'willsnow']])
print(decision.score(test[labels_class],
               test[['willrain']]))#,'willsnow']]))
prediction = decision.predict(test[labels_class])

fig, ax = plt.subplots()
days = np.arange(len(test))+1.
ax.plot(days, test.precip1.values, label='rain')
ax.plot(days, test.snow.values, label='snow')
ax.plot(days, prediction)
#ax.plot(days, prediction[1])
ax.legend()
ax.set_xlim(1,32)
fig.show()
