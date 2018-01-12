month_ticks = []
accum = 0
for days in [0,31,28,31,30,31,30,31,31,30,31,30,31]:
    accum += days
    month_ticks.append(accum)
month_label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

plt.cm.get_cmap('viridis')
colors = [cmap(.1*i) for i in range(10)]
