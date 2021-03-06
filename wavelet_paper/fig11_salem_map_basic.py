import salem
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
import pdb

fpath = '/localscratch/wllf030/cornkle/obs_data/blob_maps_MSG/'
file = fpath + 'blob_map_90km_sum_18UTC.nc'
file2 = fpath + 'blob_map_30km_sum_18UTC.nc'
file3 = fpath + 'blob_map_90km_sum_3UTC.nc'
file4 = fpath + 'blob_map_30km_sum_3UTC.nc'
tpath = '/users/global/cornkle/data/pythonWorkspace/proj_CEH/topo/gtopo_1min_afr.nc'
spath = '/users/global/cornkle/C_paper/wavelet/figs/paper/'

diff30 = fpath + 'blob_map_30km_18-3UTRC_diff.nc'
diff90 = fpath + 'blob_map_90km_18-3UTRC_diff.nc'

ds = xr.open_dataarray(file)
top = xr.open_dataarray(tpath)
ds2 = xr.open_dataarray(file2)
ds3 = xr.open_dataarray(file3)
ds4 = xr.open_dataarray(file4)

d30diff = xr.open_dataarray(diff30)
d90diff = xr.open_dataarray(diff90)


ds.name = '100k'
ds2.name = '30k'

ds = ds.sel(lon=slice(-17.5,20), lat=slice(4.5,20))  # lake chad lon=slice(10,20), lat=slice(10,15)
ds2 = ds2.sel(lon=slice(-17.5,20), lat=slice(4.5,20))   # volta lon=slice(-10,8), lat=slice(4,10)
ds3 = ds3.sel(lon=slice(-17.5,20), lat=slice(4.5,20))
ds4 = ds4.sel(lon=slice(-17.5,20), lat=slice(4.5,20))
top = top.sel(lon=slice(-17.5,20), lat=slice(4.5,20))

grid = ds.salem.grid
srtm_on_ds = ds.salem.lookup_transform(top)

ds[ds == 0]=np.nan
ds2[ds2 == 0] =np.nan
ds3[ds3 == 0] =np.nan
ds4[ds4 == 0] =np.nan

# ds[srtm_on_ds == 0]=np.nan
# ds2[srtm_on_ds == 0] =np.nan
# ds3[srtm_on_ds == 0] =np.nan
# ds4[srtm_on_ds == 0] =np.nan

perc = ds.quantile(0.99)
perc2 =ds2.quantile(0.99)
perc3 =ds3.quantile(0.99)
perc4 =ds4.quantile(0.99)

# perc = np.max(ds)
# perc2 =np.max(ds2)
# perc3 =np.max(ds3)
# perc4 =np.max(ds4)

# percc = np.max([perc,perc3])
# percc1 = np.max([perc2, perc4])
#
# ds = (ds-1) / (percc- 1)  # dim=['lon']
# ds2 = (ds2-1) / (percc1- 1)
# ds3 = (ds3-1) / (percc- 1)
# ds4 = (ds4-1) / (percc1- 1)

dsr = (ds-1) / (perc- 1)  # dim=['lon']
ds2r = (ds2-1) / (perc2- 1)
ds3r = (ds3-1) / (perc3- 1)
ds4r = (ds4-1) / (perc4- 1)
#
# dsr = dsr.where(ds<=1)
# ds2r = ds2r.where(ds2<=1)
# ds3r = ds3r.where(ds3<=1)
# ds4r = ds4r.where(ds4<=1)

# ds[ds.where(ds<=1)]=-999
# ds2[ds2 > 1]=-999
# ds3[ds3 > 1]=-999
# ds4[ds4 > 1]=-999

# fact90 = np.sum(ds3)/np.sum(ds)
# fact30 = np.sum(ds4)/np.sum(ds2)
#
# dsr = ds *fact90
# ds2r = ds2 * fact30
# ds3r = ds3
# ds4r = ds4

map = ds.salem.get_map(cmap='Greys')
map.set_shapefile(rivers=True)
# read the ocean shapefile (data from http://www.naturalearthdata.com)
oceans = salem.read_shapefile(salem.get_demo_file('ne_50m_ocean.shp'),
                              cached=True)

lakes = salem.read_shapefile(salem.get_demo_file('ne_50m_lakes.shp'), cached=True)
map.set_shapefile(lakes, edgecolor='k', facecolor='none', linewidth=2,)

#
# f,((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4,2,figsize = (18,15))

f,((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3,2,figsize = (11,7.5))


map.set_plot_params(levels=np.arange(0,81,10), cmap='viridis_r')
#map.set_plot_params(levels=[-100,-75,-50,-40,-30,30,40,50,75,100], cmap='RdBu')
# d90diff = d90diff.values
# d90diff[d90diff<0]=d90diff[d90diff<0]*1.1
# pdb.set_trace()
dat = ds

map.set_data(dat)
map.set_lonlat_contours(add_ytick_labels=False)
map.visualize(ax=ax2, addcbar=False) #, title='>90km 1800UTC - 0300UTC'
# d30diff = d30diff.values
# d30diff[d30diff<0]=d30diff[d30diff<0]*1.1
dat = ds2*2

map.set_data(dat)
map.set_lonlat_contours(add_ytick_labels=True)
map.visualize(ax=ax1,  addcbar=False) #title='<35km 1800UTC - 0300UTC',
kw2 = map.get_colorbarbase_kwargs()

for tick in ax1.xaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax2.xaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax1.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax2.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)



map.set_plot_params(levels=[-40, -20, -10, 10,20, 40], cmap='RdBu')
#map.set_plot_params(levels=[-100,-75,-50,-40,-30,30,40,50,75,100], cmap='RdBu')
dat =d90diff-4
print(np.nansum(dat))

map.set_data(dat)
map.set_lonlat_contours(add_ytick_labels=False)
map.visualize(ax=ax4, addcbar=False) #, title='>90km 1800UTC - 0300UTC'

dat = d30diff*2-4
print(np.nansum(dat))

map.set_data(dat)
map.set_lonlat_contours(add_ytick_labels=True)
map.visualize(ax=ax3,  addcbar=False) #title='<35km 1800UTC - 0300UTC',
kw3 = map.get_colorbarbase_kwargs()

for tick in ax3.xaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax4.xaxis.get_major_ticks():
                tick.label.set_fontsize(9)
for tick in ax3.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax4.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)


zuse = map.set_topography(top, relief_factor=1.4)
map.set_lonlat_contours(add_ytick_labels=True)
map.set_plot_params(vmax=2000, cmap='topo')
map.set_data(zuse)
map.visualize(ax=ax5, addcbar=False) #, title='Topography'
for tick in ax5.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)
for tick in ax5.xaxis.get_major_ticks():
                tick.label.set_fontsize(8)
kw = map.get_colorbarbase_kwargs()

ax6.axis('off')


fsiz = 13
x = 0.01
x2 = 0.50
plt.annotate('a)', xy=(x, 0.97), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
plt.annotate('b)', xy=(x2, 0.97), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
plt.annotate('c)', xy=(x, 0.65), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
plt.annotate('d)', xy=(x2, 0.65), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
plt.annotate('e)', xy=(x, 0.32), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')



plt.tight_layout()

f.subplots_adjust(right=0.89)
# cax = f.add_axes([0.95,0.55,0.025,0.4])
# salem.DataLevels(ds, nlevels=8)
# #kw1=salem.DataLevels.colorbarbase(cax, **kw1)
# mpl.colorbar.ColorbarBase(cax, **kw1)

cax = f.add_axes([0.90,0.39,0.017,0.25])
dl=salem.DataLevels(ds, nlevels=8)
#kw1=salem.DataLevels.colorbarbase(cax, **kw1)
cb1 = mpl.colorbar.ColorbarBase(cax, label ='Nocturnal   |   Afternoon' , **kw3)
#dl.set_extend(extend='both')
#cb1.set_ticklabels(['']*6)
#f.colorbar(cax).set_yticklabels(['','','','','',''])


cax = f.add_axes([0.46,0.07,0.017,0.25])
mpl.colorbar.ColorbarBase(cax, label='m', **kw)

cax = f.add_axes([0.9,0.72,0.017,0.25])
mpl.colorbar.ColorbarBase(cax, label='Frequency', **kw2)

plt.savefig(spath+'/scales_map.png', dpi=300)


