import matplotlib.pyplot as plt
month_ticks = []
accum = 0
for days in [0,31,28,31,30,31,30,31,31,30,31,30,31]:
    accum += days
    month_ticks.append(accum)
month_label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

cmap = plt.cm.get_cmap('viridis')
colors = [cmap(float(i)/float(9)) for i in range(10)] # purple -> 
#      0             1            2     3     4      5      6         7             8       9
# purple, light purple, blue-purple, blue, blue, green, green, greenish, green-yellow, yellow
print(len(colors))
