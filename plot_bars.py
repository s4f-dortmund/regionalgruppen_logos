import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import pandas as pd

plt.rcParams['font.family'] = 'Open Sans'

URL = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'

df = pd.read_csv(
    URL,
    skiprows=1,
    index_col=0,
    na_values='***',
)
year_mean = df['J-D'].dropna()


fig = plt.figure(figsize=(4, 4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()


cmap = plt.get_cmap('RdBu_r')

rectangles = [Rectangle((year, 0), 1, 1) for year in year_mean.index]
col = PatchCollection(rectangles)
col.set_array(year_mean)
col.set_cmap(cmap)
ax.add_collection(col)

ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_xlim(1880, 2019)
fig.savefig('build/bars.pdf')
