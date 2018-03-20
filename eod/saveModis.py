# -*- coding: utf-8 -*-


import multiprocessing
import glob
from eod import rewrite_data
import pdb
import os
import xarray as xr
import numpy as np
import pandas as pd

def saveNetcdf():

    modis_folder = '/users/global/cornkle/data/OBS/modis_LST/modis_raw_binary'
    pool = multiprocessing.Pool(processes=7)
    files = glob.glob(modis_folder+'/lsta_daily_2*.gra')

    for f in files:
        ds = rewrite_data.rewriteModis_toNetcdf(f, write=True)


def saveDailyBlobs():

    msgfile = '/users/global/cornkle/MCSfiles/blob_map_allscales_-50_JJAS_points_dominant.nc'
    msg = xr.open_dataarray(msgfile)

    # def first_nozero(array_like, axis):
    #     array_like[array_like<16]= array_like[array_like<16]+24
    #     return np.nanmin(array_like,axis=axis)

    msg.values[msg.values > 75] = np.nan
    msg.values[msg.values == 0] = np.nan

    for m in msg:
        if m['time.hour'].values >= 16:
            m.values[m > 0] = m['time.hour'].values
        else:
            m.values[m > 0] = m['time.hour'].values+24

    ### this is useful, it removes all pixels which got rain twice on a day
    md = msg.resample('24H', base=16, dim='time', skipna=True, how='min')

    md = md[(md['time.month'] >=6) & (md['time.month'] <=9)]
    pdb.set_trace()
    md.values[md.values>23] = md.values[md.values>23]-24

    md.to_netcdf('/users/global/cornkle/MCSfiles/blob_map_allscales_-50_JJAS_points_dominant_daily.nc')


def saveNetcdf_blobs():

    modis_folder = '/users/global/cornkle/data/OBS/modis_LST/modis_raw_binary'
    td = pd.Timedelta('16 hours')
    files = glob.glob(modis_folder + '/lsta_daily_2*.gra')

    msgfile = '/users/global/cornkle/MCSfiles/blob_map_allscales_-50_JJAS_points_dominant_daily.nc'
    msg = xr.open_dataarray(msgfile)



    for f in files:
        ds,out = rewrite_data.rewriteModis_toNetcdf(f, write=False)
        ds['LSTA'].values[ds['LSTA'].values < -800] = np.nan
        ds['LSTA'].values = ds['LSTA'].values - np.nanmean(ds['LSTA'].values)

        m = msg[(msg['time']-td).values==ds['time'].values]
        m = m.sel(lat=slice(10.3,19.7), lon=slice(-9.7,9.7))

        ds['cell'] = ds['LSTA'].copy()*np.nan

        pos = np.where((m.values > 5) )
        if np.sum(pos) == 0:
            print('No blobs found')
            try:
                ds.to_netcdf(out)
            except OSError:
                print('Did not find ' + out)
                print('Out directory not found')
            print('Wrote ' + out)
            continue

        for y, x in zip(pos[1], pos[2]):
            lat = m['lat'][y]
            lon = m['lon'][x]

            point = ds.sel(lat=lat, lon=lon, method='nearest')
            plat = point['lat'].values
            plon = point['lon'].values

            xpos = np.where(ds['lon'].values == plon)
            xpos = int(xpos[0])
            ypos = np.where(ds['lat'].values == plat)
            ypos = int(ypos[0])

            ds['cell'].values[0,ypos,xpos] = m.values[0,y,x]

        try:
            ds.to_netcdf(out)
        except OSError:
            print('Did not find ' + out)
            print('Out directory not found')
        print('Wrote ' + out)
















def saveClimNetcdf():

    modis_folder = '/users/global/cornkle/data/OBS/modis_LST/modis_raw_binary'
    pool = multiprocessing.Pool(processes=7)
    files = glob.glob(modis_folder+'/seasonal*.gra')

    #res = pool.map(rewrite_data.rewriteGridsat_toNetcdf, files)
    #res = pool.map(rewrite_data.rewriteModis_toNetcdf, files)

    for f in files:
        rewrite_data.rewriteModisClim_toNetcdf(f)
