# -*- coding: utf-8 -*-


import numpy as np
from wavelet import util
from eod import msg
import xarray as xr
import os
from utils import u_grid, u_interpolate as u_int
import multiprocessing
import datetime as dt
import matplotlib.pyplot as plt
import pdb
from scipy.ndimage.measurements import label


def run():
    #  (1174, 378)
    msg_folder = '/users/global/cornkle/data/OBS/meteosat_WA30'
    pool = multiprocessing.Pool(processes=6)

    m = msg.ReadMsg(msg_folder, y1=2006, y2=2010)
    files  = m.fpath

    #files = files[1050:1057]
    mdic = m.read_data(files[0], llbox=[-11, 11, 9, 20])
    # make salem grid
    grid = u_grid.make(mdic['lon'].values, mdic['lat'].values, 5000) #m.lon, m.lat, 5000)
    inds, weights, shape = u_int.interpolation_weights_grid(mdic['lon'].values, mdic['lat'].values, grid)
    gridd = (inds,weights,shape, grid)

    files_str = []

    for f in files:
        files_str.append(f[0:-6])

    files_str = np.unique(files_str)

    passit = []
    for f in files_str:
        passit.append((gridd,m, f))

    res = pool.map(file_loop, passit)

    # for l in passit:
    #
    #     test = file_loop(l)

    pool.close()

    res = [x for x in res if x is not None]

    da = xr.concat(res, 'time')
    savefile = '/users/global/cornkle/MCSfiles/blob_map_JJAS_-70minT_15k.nc'

    try:
        os.remove(savefile)
    except OSError:
        pass
    da.name = 'blob'
    #enc = {'blob': {'complevel': 5, 'zlib': True}}
    da.to_netcdf(path=savefile)#, mode='w', encoding=enc, format='NETCDF4')

    print('Saved ' + savefile)



def file_loop(passit):


    gridd = passit[0]
    inds = gridd[0]
    weights = gridd[1]
    shape = gridd[2]
    grid = gridd[3]

    m = passit[1]
    files = passit[2]

    min = '00'

    strr = files.split(os.sep)[-1]

    if ((np.int(strr[4:6]) > 9) | (np.int(strr[4:6])<6)):
        print('Skip month')
        return

    if not ((np.int(strr[8:10]) >= 17) | (np.int(strr[8:10]) <= 3)): #& (np.int(strr[8:10]) <= 19) ): #((np.int(strr[8:10]) > 3)): #not ((np.int(strr[8:10]) >= 16) & (np.int(strr[8:10]) <= 19) ): #& (np.int(strr[8:10]) < 18): #(np.int(strr[4:6]) != 6) & #(np.int(strr[8:10]) != 3) , (np.int(strr[8:10]) > 3)
        print('Skip hour')
        return

    lon, lat = grid.ll_coordinates

    file = files+min+'.gra'

    print('Doing file: ' + file)
    try:
        mdic = m.read_data(file, llbox=[-11, 11, 9, 20])
    except FileNotFoundError:
        print('File not found')
        return

    if not mdic:
        print('File missing')
        return
    hour = mdic['time.hour']
    minute = mdic['time.minute' ]
    day = mdic['time.day']
    month = mdic['time.month']
    year = mdic['time.year']

    date = dt.datetime(year, month, day, hour, minute)

    outt = u_int.interpolate_data(mdic['t'].values, inds, weights, shape)

    figure = np.zeros_like(outt)

    outt[outt > -70] = 0
    outt[np.isnan(outt)] = 0

    labels, numL = label(outt)

    u, inv = np.unique(labels, return_inverse=True)
    n = np.bincount(inv)

    badinds = u[(n < 600)]  # all blobs with more than 36 pixels = 18 km x*y = 324 km2 (meteosat ca. 3km)
    goodinds = u[(n >= 600)]

    for bi in badinds:
        inds = np.where(labels == bi)
        outt[inds] = 0

    for gi in goodinds:

        if gi == 0:
            continue

        dummy = np.zeros_like(outt)

        pos = np.where(labels == gi)
        dummy[pos] = outt[pos]
        ismin = np.argmin(dummy)

        if outt.flat[ismin] <= -70:
            figure.flat[ismin] = outt.flat[ismin]

    da = xr.DataArray(figure, coords={'time': date, 'lat': lat[:,0], 'lon':lon[0,:]}, dims=['lat', 'lon']) #[np.newaxis, :]

    print('Did ', file)

    return (da)

