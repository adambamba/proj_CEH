import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from utils import u_darrays
import pdb
from utils import constants_lappi as cnst
import salem
from utils import u_statistics as us
from scipy import stats
import numpy.ma as ma
import pickle as pkl

def trend_all():

    srfc = cnst.ERA_MONTHLY_SRFC
    pl = cnst.ERA_MONTHLY_PL
    mcs = cnst.GRIDSAT + 'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = cnst.network_data + 'figs/CLOVER/months/'

    box=[-18,40,0,25]
    #box=[-18,55,-45,45]
    #box = [-8, -4, 5.5, 7.5]

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))#latitude=slice(36, -37))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))#latitude=slice(36, -37))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(box[0], box[1]), lat=slice(box[2],box[3]))

    lons = da.longitude
    lats = da.latitude

    #q = da['q'].sel(level=925)
    q = da['q'].sel(level=650)
    #q = da2['tcwv']
    t2d = da['t'].sel(level=925)

    u925 = da['u'].sel(level=925)#).mean(dim='level')  #slice(850
    u600 = da['u'].sel(level=650)

    shear = u600-u925

    q.values = q.values*1000

    grid = t2d.salem.grid.regrid(factor=0.5)
    t2 = grid.lookup_transform(t2d)
    tir = grid.lookup_transform(da3['tir'])
    q = grid.lookup_transform(q)

    shear = grid.lookup_transform(shear)

    # tir = t2d.salem.lookup_transform(da3['tir'])
    #
    # t2 = t2d
    # #tir = da3['tir']
    # q = q
    # shear = shear

    grid = grid.to_dataset()

    t2 = xr.DataArray(t2, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    q = xr.DataArray(q, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    tir = xr.DataArray(tir, coords=[da3['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    shear = xr.DataArray(shear, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])

    #months = np.arange(1,13)
    months=[3,4,5,10]

    dicm = {}

    def array_juggling(data, month, hour=None):

        m = month

        if hour!=None:
            data = data[((data['time.month'] >= 3) & (data['time.month'] <= 5)) & (data['time.hour'] == hour)]
        else:
            data = data[(data['time.month'] >= 3) & (data['time.month'] <= 5)]
        data_years = data.groupby('time.year').mean(axis=0)

        # stack lat and lon into a single dimension called allpoints
        datastacked = data_years.stack(allpoints=['latitude', 'longitude'])

        # apply the function over allpoints to calculate the trend at each point
        print('Entering trend calc')
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend_mk, alpha=0.05, eps=0.0001)

        ddtrend = dtrend['slope']
        try:
            pthresh = us.fdr_threshold(dtrend['pval'].values[np.isfinite(dtrend['pval'].values)], alpha=0.05)
            ddtrend.values[(dtrend['pval'].values > pthresh) | np.isnan(dtrend['pval'].values)] = np.nan
        except ValueError:
            ddtrend.values = ddtrend.values*np.nan
            pthresh = np.nan
        print('p value threshold', pthresh)

        # unstack back to lat lon coordinates
        return ddtrend.unstack('allpoints'), data_years

    for m in months:

        tirtrend, dyears = array_juggling(tir, m)
        tirm_mean = dyears.mean(axis=0)

        t2trend, dummy = array_juggling(t2, m) #, hour=12

        qtrend, dummy = array_juggling(q, m) #, hour=12

        sheartrend, dummy = array_juggling(shear, m) #, hour=12

        t2trend_unstacked = t2trend*10. # warming over decade
        qtrend_unstacked = qtrend * 10.  # warming over decade
        sheartrend_unstacked = sheartrend * 10.  # warming over decade
        tirtrend_unstacked = ((tirtrend.values)*10. / tirm_mean.values) * 100.

        dicm[m] = tirtrend_unstacked

        t_da = t2trend_unstacked #xr.DataArray(t2trend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        q_da = qtrend_unstacked #xr.DataArray(qtrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        s_da = sheartrend_unstacked #xr.DataArray(sheartrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        ti_da = tirtrend_unstacked #xr.DataArray(tirtrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])

        fp = fpath + 'ttrend_mktrend_-70C_coarse_FIRSTSEASON'+str(m).zfill(2)+'.png'#'ttrend_synop_-70C_coarse_'+str(m).zfill(2)+'.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)

        # map.set_shapefile(rivers=True)
        map.set_plot_params()

        map.set_data(t_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu_r', extend='both')
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(q_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu', extend='both')
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(s_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-1,1.1,0.2), cmap='RdBu', extend='both')
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(ti_da)  # interp='linear'
        map.set_plot_params(cmap='Blues', extend='both', levels=np.arange(20,101,20)) #levels=np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.savefig(fp)
        plt.close('all')

    pkl.dump(dicm,
             open(cnst.network_data + 'data/CLOVER/saves/storm_frac.p',
                  'wb'))

def trend_all_polyfit():
    srfc = cnst.ERA_MONTHLY_SRFC
    pl = cnst.ERA_MONTHLY_PL
    mcs = cnst.GRIDSAT+'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = '/users/global/cornkle/figs/CLOVER/months/'

    box=[-18,40,0,30]
    #box = [-8, -4, 5.5, 7.5]

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))#latitude=slice(36, -37))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))#latitude=slice(36, -37))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(box[0], box[1]), lat=slice(box[2],box[3]))

    lons = da.longitude
    lats = da.latitude

    q = da['q'].sel(level=925)
    qdry = da['q'].sel(level=650)
    #q = da2['tcwv']
    t2d = da['t'].sel(level=925)

    u925 = da['u'].sel(level=925)#).mean(dim='level')  #slice(850
    u600 = da['u'].sel(level=650)

    shear = u600-u925

    q.values = q.values*1000

    grid = t2d.salem.grid.regrid(factor=0.5)
    t2 = grid.lookup_transform(t2d)
    tir = grid.lookup_transform(da3['tir'])
    q = grid.lookup_transform(q)
    qdry =  grid.lookup_transform(q)
    shear = grid.lookup_transform(shear)

    # tir = t2d.salem.lookup_transform(da3['tir'])
    #
    # t2 = t2d
    # #tir = da3['tir']
    # q = q
    # shear = shear

    grid = grid.to_dataset()

    t2 = xr.DataArray(t2, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    q = xr.DataArray(q, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    tir = xr.DataArray(tir, coords=[da3['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    shear = xr.DataArray(shear, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])

    months = np.arange(1,13)
    #months=[10]

    def array_juggling(data, month, hour=None):

        m = month

        if hour!=None:
            data = data[(data['time.month'] == m) & (data['time.hour'] == hour)]
        else:
            data = data[(data['time.month'] == m)]

        data_years = data.groupby('time.year').mean(axis=0)

        # stack lat and lon into a single dimension called allpoints
        datastacked = data_years.stack(allpoints=['latitude', 'longitude'])

        # apply the function over allpoints to calculate the trend at each point

        print('Entering trend calc')
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend)#_trend_mk, alpha=0.05, eps=0.0001)
        #dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend)
        ddtrend = dtrend['slope']

        # unstack back to lat lon coordinates
        return ddtrend.unstack('allpoints'), data_years

    for m in months:
        tirtrend, dyears = array_juggling(tir, m)
        tirm_mean = dyears.mean(axis=0)
        t2trend, dummy = array_juggling(t2, m) #, hour=12

        qtrend, dummy = array_juggling(q, m) #, hour=12

        sheartrend, dummy = array_juggling(shear, m) #, hour=12


        t2trend_unstacked = t2trend*10. # warming over decade
        qtrend_unstacked = qtrend * 10.  # warming over decade
        sheartrend_unstacked = sheartrend * 10.  # warming over decade
        tirtrend_unstacked = ((tirtrend.values)*10. ) * 100. / tirm_mean.values

        t_da = t2trend_unstacked #xr.DataArray(t2trend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        q_da = qtrend_unstacked #xr.DataArray(qtrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        s_da = sheartrend_unstacked #xr.DataArray(sheartrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])
        ti_da = tirtrend_unstacked #xr.DataArray(tirtrend_unstacked, coords=[lats, lons], dims=['latitude', 'longitude'])


        fp = fpath + 'ttrend_linear_-70C_coarse_u_srfc'+str(m).zfill(2)+'.png' #'MCS_trend_10_TEST_mk.png'#
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)

        # map.set_shapefile(rivers=True)
        map.set_plot_params()

        map.set_data(t_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu_r', extend='both')
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(q_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu', extend='both')
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(s_da)  # interp='linear'
        map.set_plot_params(levels=np.arange(-1,1.1,0.2), cmap='RdBu', extend='both')
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(ti_da)  # interp='linear'
        map.set_plot_params(cmap='Blues', extend='both') #levels=np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.savefig(fp)
        plt.close('all')



def corr_all():
    srfc = cnst.ERA_MONTHLY_SRFC_SYNOP
    pl = cnst.ERA_MONTHLY_PL_SYNOP
    mcs = cnst.GRIDSAT+'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = '/users/global/cornkle/figs/CLOVER/months/'

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(-18, 40), latitude=slice(0,25))#latitude=slice(36, -37))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(-18, 40), latitude=slice(0,25))#latitude=slice(36, -37))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(-18, 40), lat=slice(0, 25))

    lons = da.longitude
    lats = da.latitude

    q = da['q'].sel(level=slice(850,925)).mean(dim='level')
    #q = da2['tcwv']
    t2 = da['t'].sel(level=925)

    u925 = da['u'].sel(level=slice(850,925)).mean(dim='level')
    u600 = da['u'].sel(level=slice(600, 650)).mean(dim='level')

    shear = u600-u925

    q.values = q.values*1000

    tir = da3['tir']
    tir = t2.salem.lookup_transform(tir)

    months = np.arange(1,13)
    #months=[6,7]

    def array_juggling(data, month, hour=None):

        m = month

        if hour!=None:
            data = data[(data['time.month'] == m) & (data['time.hour'] == hour) & (data['time.year'] >=1983) & (data['time.year'] <=2013) & (data['time.year'] !=2003)]
        else:
            data = data[(data['time.month'] == m) & (data['time.year'] >=1983) & (data['time.year'] <=2013) & (data['time.year'] !=2003)]
        data_years = data.groupby('time.year').mean(axis=0)

        diff = xr.DataArray(data_years.values[1::, :, :] - data_years.values[0:-1, :, :], coords=[data_years.year[1::], data.latitude, data.longitude], dims=['year','latitude', 'longitude'] )

        # unstack back to lat lon coordinates
        return  diff, data_years

    months=[9,10]
    for m in months:

        t2diff, t2year = array_juggling(t2, m, hour=12)
        qdiff, qyear= array_juggling(q, m, hour=12)
        shdiff, sheyear = array_juggling(shear, m, hour=12)
        tirdiff, tiryear = array_juggling(tir, m)

        def corr(a,b):
            ds = xr.Dataset()
            ds['pval'] = a.copy(deep=True).sum('year')*np.nan
            ds['r'] = a.copy(deep=True).sum('year')*np.nan


            for lat in a.latitude.values:
                for lon in a.longitude.values:
                    aa = a.sel(latitude=lat, longitude=lon)
                    bb = b.sel(latitude=lat, longitude=lon)

                    r, p = stats.pearsonr(aa.values, bb.values)

                    if np.nansum(aa.values == 0) >= 10:

                        p = np.nan
                        r = np.nan

                    ds['r'].loc[{'latitude':lat, 'longitude':lon}] = r
                    ds['pval'].loc[{'latitude':lat, 'longitude':lon}] = p

            return ds

        qcorr = corr(tirdiff, qdiff)
        shearcorr = corr(tirdiff, shdiff)
        tcorr = corr(tirdiff ,t2diff)

        #pthresh = us.fdr_threshold(qcorr['pval'].values[np.isfinite(qcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        pthresh = 0.05
        qcorr['r'].values[qcorr['pval'].values > pthresh] = np.nan

        #pthresh = us.fdr_threshold(shearcorr['pval'].values[np.isfinite(shearcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        shearcorr['r'].values[shearcorr['pval'].values > pthresh] = np.nan

       # pthresh = us.fdr_threshold(tcorr['pval'].values[np.isfinite(tcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        tcorr['r'].values[tcorr['pval'].values > pthresh] = np.nan


        fp = fpath + 'corr_synop_'+str(m).zfill(2)+'.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)

        # map.set_shapefile(rivers=True)
        map.set_plot_params()

        map.set_data(tcorr['r'])  # interp='linear'
        map.set_contour(t2year.mean('year')-273.15)
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu', extend='both')
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(qcorr['r'])  # interp='linear'
        map.set_contour(qyear.mean('year'))
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu', extend='both')
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(shearcorr['r'])  # interp='linear'
        map.set_contour(sheyear.mean('year'))
        map.set_plot_params(levels=np.arange(-0.5,0.51,0.1), cmap='RdBu', extend='both')
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(shearcorr['r'])  # interp='linear'
        map.set_plot_params(cmap='Blues', extend='both', levels=np.arange(20,101,20)) #levels=np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.savefig(fp)
        plt.close('all')


def slope_box():
    srfc = cnst.ERA_MONTHLY_SRFC_SYNOP
    pl = cnst.ERA_MONTHLY_PL_SYNOP
    mcs = cnst.GRIDSAT+'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = '/users/global/cornkle/figs/CLOVER/months/'

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(-18, 40), latitude=slice(0,25))#latitude=slice(36, -37))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(-18, 40), latitude=slice(0,25))#latitude=slice(36, -37))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(-18, 40), lat=slice(0, 25))

    lons = da.longitude
    lats = da.latitude

    q = da['q'].sel(level=slice(850,925)).mean(dim='level')
    #q = da2['tcwv']
    t2 = da['t'].sel(level=925)

    u925 = da['u'].sel(level=slice(850,925)).mean(dim='level')
    u600 = da['u'].sel(level=slice(600, 650)).mean(dim='level')

    shear = u600-u925

    q.values = q.values*1000

    tir = da3['tir']
    tir = t2.salem.lookup_transform(tir)

    months = np.arange(1,13)
    months=[3,4,5,6]

    def array_juggling(data, month, hour=None):

        m = month

        if hour!=None:
            data = data[(data['time.month'] == m) & (data['time.hour'] == hour) & (data['time.year'] >=1983) & (data['time.year'] <=2013) & (data['time.year'] !=2003)]
        else:
            data = data[(data['time.month'] == m) & (data['time.year'] >=1983) & (data['time.year'] <=2013) & (data['time.year'] !=2003)]
        data_years = data.groupby('time.year').mean(axis=0)

        #diff = xr.DataArray(data_years.values[1::, :, :] - data_years.values[0:-1, :, :], coords=[data_years.year[1::], data.latitude, data.longitude], dims=['year','latitude', 'longitude'] )
        diff = xr.DataArray(data_years.values, coords=[data_years.year, data.latitude, data.longitude], dims=['year', 'latitude', 'longitude'])
        # unstack back to lat lon coordinates
        return  diff, data_years

    def corr(a, b):
        ds = xr.Dataset()
        ds['pval'] = a.copy(deep=True).sum('year') * np.nan
        ds['r'] = a.copy(deep=True).sum('year') * np.nan
        ds['slope'] = a.copy(deep=True).sum('year') * np.nan

        aa = a.sel(latitude=slice(4,8), longitude=slice(-10,11)).mean(dim=['latitude', 'longitude'])

        for lat in a.latitude.values:
            for lon in a.longitude.values:

                bb = b.sel(latitude=lat, longitude=lon)

                r, p = stats.pearsonr(aa.values, bb.values)
                pf = np.polyfit(aa.values, bb.values, 1)
                slope = pf[0]

                # if (np.nansum(aa.values == 0) >= 10):
                #     p = np.nan
                #     r = np.nan

                ds['r'].loc[{'latitude': lat, 'longitude': lon}] = r
                ds['pval'].loc[{'latitude': lat, 'longitude': lon}] = p
                ds['slope'].loc[{'latitude': lat, 'longitude': lon}] = slope

        return ds

    for m in months:

        t2diff, t2year = array_juggling(t2, m, hour=12)
        qdiff, qyear= array_juggling(q, m, hour=12)
        shdiff, sheyear = array_juggling(shear, m, hour=12)
        tirdiff, tiryear = array_juggling(tir, m)

        qcorr = corr(tirdiff, qdiff)
        shearcorr = corr(tirdiff, shdiff)
        tcorr = corr(tirdiff ,t2diff)

        #pthresh = us.fdr_threshold(qcorr['pval'].values[np.isfinite(qcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        pthresh = 0.01

        qcorr['slope'].values[qcorr['pval'].values > pthresh] = np.nan

        #pthresh = us.fdr_threshold(shearcorr['pval'].values[np.isfinite(shearcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        shearcorr['slope'].values[shearcorr['pval'].values > pthresh] = np.nan

       # pthresh = us.fdr_threshold(tcorr['pval'].values[np.isfinite(tcorr['pval'].values)], alpha=0.05)
        #print(pthresh)
        tcorr['slope'].values[tcorr['pval'].values > pthresh] = np.nan

        tplot = ((tirdiff.values) * 10. / tiryear.values) * 100.


        fp = fpath + 'slope_synop_'+str(m).zfill(2)+'.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)

        # map.set_shapefile(rivers=True)
        map.set_plot_params()

        map.set_data(tcorr['slope'])  # interp='linear'
        #map.set_contour(t2year.mean('year')-273.15)
        map.set_plot_params(cmap='RdBu', extend='both', vmin=-3, vmax=3)  #levels=np.arange(-0.5,0.51,0.1),
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(qcorr['slope'])  # interp='linear'
        #map.set_contour(qyear.mean('year'))
        map.set_plot_params( cmap='RdBu', extend='both', vmin=-4, vmax=4)  #levels=np.arange(-0.5,0.51,0.1),
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(shearcorr['slope'])  # interp='linear'
        #map.set_contour(sheyear.mean('year'))
        map.set_plot_params(cmap='RdBu', extend='both', vmin=-4, vmax=4)  #levels=np.arange(-0.5,0.51,0.1)
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(tirdiff.mean('year'))  # interp='linear'
        map.set_plot_params(cmap='Blues', extend='both', vmax=3) #levels=np.arange(20,101,20)  #np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.savefig(fp)
        plt.close('all')


def corr_box():
    srfc = cnst.ERA_MONTHLY_SRFC_SYNOP
    pl = cnst.ERA_MONTHLY_PL_SYNOP
    mcs = cnst.GRIDSAT + 'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = cnst.network_data + 'figs/CLOVER/months/'

    dicm = pkl.load(open(cnst.network_data + 'data/CLOVER/saves/storm_frac.p', 'rb'))

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(-18, 40), latitude=slice(0, 25))  # latitude=slice(36, -37))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(-18, 40), latitude=slice(0, 25))  # latitude=slice(36, -37))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(-18, 40), lat=slice(0, 25))

    lons = da.longitude
    lats = da.latitude

    q = da['q'].sel(level=slice(850, 925)).mean(dim='level')
    # q = da2['tcwv']
    t2 = da['t'].sel(level=925)

    u925 = da['v'].sel(level=925)#.mean(dim='level') c#slice(850,
    u600 = da['u'].sel(level=slice(600, 650)).mean(dim='level')

    shear =  u925

    q.values = q.values * 1000

    tir = da3['tir']
    tir = t2.salem.lookup_transform(tir)

    months = np.arange(1, 13)
    months = [3,4,5,6,10]

    def array_juggling(data, month, hour=None):

        m = month

        if hour != None:
            data = data[(data['time.month'] == m) & (data['time.hour'] == hour) & (data['time.year'] >= 1983)& (
            data['time.year'] <= 2017)]
        else:
            data = data[(data['time.month'] == m) & (data['time.year'] >= 1983) & (data['time.year'] <= 2017)]
        data_years = data.groupby('time.year').mean(axis=0)

        data_mean = data.mean(axis=0)

        # diff = xr.DataArray(data_years.values[1::, :, :] - data_years.values[0:-1, :, :], coords=[data_years.year[1::], data.latitude, data.longitude], dims=['year','latitude', 'longitude'] )
        diff = xr.DataArray(data_years.values, coords=[data_years.year, data.latitude, data.longitude],
                            dims=['year', 'latitude', 'longitude'])
        # unstack back to lat lon coordinates
        return diff, data_mean

    def corr(a, b, single=None):
        ds = xr.Dataset()
        ds['pval'] = a.copy(deep=True).sum('year') * np.nan
        ds['r'] = a.copy(deep=True).sum('year') * np.nan
        ds['slope'] = a.copy(deep=True).sum('year') * np.nan

        aa = a.sel(latitude=slice(4, 8), longitude=slice(-10, 11)).mean(dim=['latitude', 'longitude'])


        for lat in a.latitude.values:
            for lon in a.longitude.values:

                if single:
                    bb = b
                    r,p = stats.pearsonr(bb, aa.values)
                    pf = np.polyfit(bb, aa.values, 1)

                else:
                    bb = b.sel(latitude=lat, longitude=lon)
                    r, p = stats.pearsonr(aa.values, bb.values)
                    pf = np.polyfit(aa.values, bb.values, 1)
                slope = pf[0]

                # if (np.nansum(aa.values == 0) >= 10):
                #     p = np.nan
                #     r = np.nan

                ds['r'].loc[{'latitude': lat, 'longitude': lon}] = r
                ds['pval'].loc[{'latitude': lat, 'longitude': lon}] = p
                ds['slope'].loc[{'latitude': lat, 'longitude': lon}] = slope

        return ds

    for m in months:
        t2diff, t2year = array_juggling(t2, m, hour=12) #
        qdiff, qyear = array_juggling(q, m, hour=12) #, hour=12
        shdiff, sheyear = array_juggling(shear, m, hour=12) #, hour=12
        tirdiff, tiryear = array_juggling(tir, m)

        qcorr = corr(tirdiff, qdiff)
        shearcorr = corr(tirdiff, shdiff)
        tcorr = corr(tirdiff, t2diff)
        cloud = corr(tirdiff, np.arange(len(tirdiff)), single=True)

        # pthresh = us.fdr_threshold(qcorr['pval'].values[np.isfinite(qcorr['pval'].values)], alpha=0.05)
        # print(pthresh)
        pthresh = 0.01
        #cloud['slope'].values[cloud['pval'].values > pthresh] = np.nan
        qcorr['r'].values[qcorr['pval'].values > pthresh] = np.nan

        # pthresh = us.fdr_threshold(shearcorr['pval'].values[np.isfinite(shearcorr['pval'].values)], alpha=0.05)
        # print(pthresh)
        shearcorr['r'].values[shearcorr['pval'].values > pthresh] = np.nan

        # pthresh = us.fdr_threshold(tcorr['pval'].values[np.isfinite(tcorr['pval'].values)], alpha=0.05)
        # print(pthresh)
        tcorr['r'].values[tcorr['pval'].values > pthresh] = np.nan

        tplot = ((cloud['slope'].values) * 10. / tiryear.values) * 100.

        fp = fpath + 'corr_synop_v_srfc' + str(m).zfill(2) + '.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)
        # map.set_shapefile(rivers=True)
        # bla = ma.masked_invalid(tcorr['r'].values)

        map.set_data(tcorr['r'].values, interp='linear')  # interp='linear'
        # map.set_contour(t2year.mean('year')-273.15)

        map.set_plot_params(cmap='RdBu_r', extend='both',levels=np.arange(-0.7,0.71,0.1))  # levels=np.arange(-0.5,0.51,0.1),
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(qcorr['r'],interp='linear')  # interp='linear'
        # map.set_contour(qyear.mean('year'))
        map.set_plot_params(cmap='RdBu_r', extend='both',levels=np.arange(-0.7,0.71,0.1))  # levels=np.arange(-0.5,0.51,0.1),
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(shearcorr['r'], interp='linear')  # interp='linear'
        # map.set_contour(sheyear.mean('year'))
        map.set_plot_params(cmap='RdBu_r', extend='both', levels=np.arange(-0.7,0.71,0.1))  # levels=np.arange(-0.5,0.51,0.1)
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(dicm[m])  # interp='linear'
        map.set_plot_params(cmap='Blues', extend='both', levels=np.arange(0.1,0.8,0.1))  # levels=np.arange(20,101,20)  #np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.tight_layout()
        plt.savefig(fp)
        plt.close('all')
