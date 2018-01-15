#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from month_marks import month_ticks, month_label, colors

# load the data
print('loading TYS_daily.h5')
dataframe = pd.read_hdf('TYS_daily.h5', 'everything').dropna()
print('total rows', len(dataframe))
dataframe.willrain = dataframe.willrain.astype(int)

# split into train and test
training = dataframe[(dataframe.index >= np.datetime64('1997-01-01')) & (dataframe.index < np.datetime64('2017-12-01'))]
test = dataframe[dataframe.index >= np.datetime64('2017-12-01')]

labels_class = ['wind_speed',
                'temp_min',
                'temp_max',
                'dew_min',
                'dew_max',
                'pressure',
                'press_change',
                'precip1',
                #'snow',
                #'water_equiv'
                ]

# run it
decision = KMeans(n_clusters=4)
decision.fit(training[labels_class],
             training[['willrain']])#,'willsnow']])
print(decision.score(test[labels_class],
               test[['willrain']]))#,'willsnow']]))
print(np.unique(decision.labels_))
prediction = decision.predict(test[labels_class])

fig, ax = plt.subplots()
days = np.arange(len(test))+365.-31
ax.plot(days, test.precip1.values, label='rain', color=colors[6])
ax.plot(days, prediction, label='prediction', color=colors[0])
ax.legend()
ax.set_title('K-means clustering (4 clusters)')
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_label)
ax.set_ylabel('rain in cm')
ax.set_xlim(334,364.5)
fig.show()
