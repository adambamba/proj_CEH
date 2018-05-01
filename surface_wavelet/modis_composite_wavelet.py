# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 10:15:40 2016

@author: cornkle
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib
import multiprocessing
import pdb
import pandas as pd
from wavelet import util
from utils import u_arrays, constants, u_met
from scipy.stats import ttest_ind as ttest
from scipy.interpolate import griddata
import pickle as pkl
import collections

matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)
matplotlib.rcParams['hatch.linewidth'] = 0.1

def run_hours():

    l = [17,18,19,0,1,2,3]
    for ll in l:
        composite(ll)


def composite(hour):
    pool = multiprocessing.Pool(processes=6)

    file = '/users/global/cornkle/MCSfiles/blob_map_allscales_-50_JJAS_points_dominant.nc'
    path = '/users/global/cornkle/figs/LSTA-bullshit/scales/new'

    hour = hour

    msg = xr.open_dataarray(file)
    msg = msg[(msg['time.hour'] == hour) & (msg['time.minute'] == 0) & (
        msg['time.year'] >= 2006) & (msg['time.year'] <= 2010) & (msg['time.month'] >= 7) ]

    msg = msg.sel(lat=slice(10.2,18.5), lon=slice(-9.7, 9.7))

    res = pool.map(file_loop, msg)
    pool.close()

    # for m in msg[2:5]:
    #     file_loop(m)
    # return
    res = [x for x in res if x is not None]

    snpos_list_dry = []
    wepos_list_dry = []

    rsnpos_list_dry = []
    rwepos_list_dry = []

    snpos_list_wet = []
    wepos_list_wet = []

    rsnpos_list_wet = []
    rwepos_list_wet = []

    for r in res:
        snpos_list_dry.append(np.squeeze(r[0]))
        wepos_list_dry.append(np.squeeze(r[1]))

        rsnpos_list_dry.append(np.squeeze(r[2]))
        rwepos_list_dry.append(np.squeeze(r[3]))


        scales = r[4]
        snpos_list_wet.append(np.squeeze(r[5]))
        wepos_list_wet.append(np.squeeze(r[6]))

        rsnpos_list_wet.append(np.squeeze(r[7]))
        rwepos_list_wet.append(np.squeeze(r[8]))


    dic = collections.OrderedDict([('SN-pos' , [snpos_list_dry, rsnpos_list_dry]),
                                   ('WE-pos' , [wepos_list_dry, rwepos_list_dry]),
                                   ('SN-pos_wet', [snpos_list_wet, rsnpos_list_wet]),
                                   ('WE-pos_wet', [wepos_list_wet, rwepos_list_wet]),
                                   ('scales' , scales)])

    keys = list(dic.keys())

    for l in keys:
        if l == 'scales':
            continue
        (dic[l])[0] = np.squeeze(np.vstack((dic[l])[0]))
        (dic[l])[1] = np.squeeze(np.vstack((dic[l])[1]))

    for l in keys:
        if l == 'scales':
            continue
        nsstat, nspvalue = ttest(dic[l][0], dic[l][1], axis=0, equal_var=False, nan_policy='omit')
        mask = nspvalue < 0.05
        dic[l].append(mask)

    for l in keys:
        if l == 'scales':
            continue

        (dic[l])[0] = np.nanmean((dic[l])[0], axis=0)
        (dic[l])[1] = np.nanmean((dic[l])[1], axis=0)


    pkl.dump(dic, open(path+"/c_wet_dry"+str(hour)+"UTC.p", "wb"))
    print('Save file written!')



def plot(hour):

    path = '/users/global/cornkle/figs/LSTA-bullshit/scales/new'
    dic = pkl.load(open(path+"/c_wet_dry"+str(hour)+"UTC.p", "rb"))


    scales = dic['scales']
    del dic['scales']

    keys = list(dic.keys())
    cnt = (dic['SN-pos'][0]).shape[0]

    # for l in keys:
    #     if keys == 'scales':
    #         continue
    #     (dic[l])[0] = np.nanmean((dic[l])[0], axis=0)
    #     (dic[l])[1] = np.nanmean((dic[l])[1], axis=0)

    l=0
    dist=100

    snblob = (dic[keys[l]])[0]#-(dic[keys[l+2]])[0]
    snrandom = (dic[keys[l]])[1]#-(dic[keys[l+2]])[1]
    snmask = (dic[keys[l]])[2]#-(dic[keys[l+2]])[2]

    weblob = (dic[keys[l+1]])[0]#-(dic[keys[l+3]])[0]
    werandom = (dic[keys[l+1]])[1]#-(dic[keys[l+3]])[1]
    wemask = (dic[keys[l+1]])[2]#-(dic[keys[l+3]])[2]

    l=2
    dist=100

    wet_snblob = (dic[keys[l]])[0]#-(dic[keys[l+2]])[0]
    wet_snrandom = (dic[keys[l]])[1]#-(dic[keys[l+2]])[1]
    wet_snmask = (dic[keys[l]])[2]#-(dic[keys[l+2]])[2]

    wet_weblob = (dic[keys[l+1]])[0]#-(dic[keys[l+3]])[0]
    wet_werandom = (dic[keys[l+1]])[1]#-(dic[keys[l+3]])[1]
    wet_wemask = (dic[keys[l+1]])[2]#-(dic[keys[l+3]])[2]

    f = plt.figure(figsize=(9, 9))
    ax = f.add_subplot(221)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales , snblob - snrandom , cmap='RdBu_r', vmin = -0.3, vmax=0.3)
    plt.colorbar(label='Power difference (Blob-random)')
    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, snmask, colors='none', hatches='.', levels = [0.5,1], linewidth=0.25)

    ax.set_xlabel('km')
    ax.set_ylabel('Scales')

    plt.title('South-North scales, Nb cores: ' + str(cnt) + '| ' + str(hour).zfill(2) + '00UTC, Jul-Sep',
              fontsize=10)

    ax = f.add_subplot(222)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3,scales,   weblob - werandom   , cmap='RdBu_r', vmin = -0.3, vmax=0.3)
    plt.colorbar(label='Power difference (Blob-random)')
    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, wemask, colors='none', hatches='.', levels = [0.5,1], linewidth=0.25)

    ax.set_xlabel('km')
    ax.set_ylabel('km')

    plt.title('West-East scales', fontsize=10)


    ax = f.add_subplot(223)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, wet_snblob - wet_snrandom   , cmap='RdBu_r', vmin = -0.4, vmax=0.4) #, vmin = -0.1, vmax=0.1)
    plt.colorbar(label='Power difference (Blob-random)')
    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, wet_snmask, colors='none', hatches='.', levels=[0.5, 1],
                 linewidth=0.25)

    ax.set_xlabel('km')
    ax.set_ylabel('Scales')

    plt.title('South-North scales, Nb cores: ' + str(cnt) + '| ' + str(hour).zfill(2) + '00UTC, Jul-Sep',
              fontsize=10)

    ax = f.add_subplot(224)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, wet_weblob - wet_werandom   , cmap='RdBu_r', vmin = -0.4, vmax=0.4) # vmin = -0.1, vmax=0.1)
    plt.colorbar(label='Power difference (Blob-random)')
    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, scales, wet_wemask, colors='none', hatches='.', levels=[0.5, 1],
                 linewidth=0.25)

    ax.set_xlabel('km')
    ax.set_ylabel('km')

    plt.title('West-East scales', fontsize=10)

    plt.tight_layout()
    #plt.savefig(path + '/lsta_hours_'+keys[l]+'_'+str(hour)+'.png')
    plt.show()


def cut_kernel(xpos, ypos, arr, date, lat, lon, rotate=False):


    dist = 100

    kernel = u_arrays.cut_kernel_3d(arr,xpos, ypos,dist)

    if (np.sum(np.isfinite(kernel)) < 0.20 * kernel.size):
        return

    #kernel3 = kernel - np.nanmean(kernel)

    if kernel.shape != (arr.shape[0], 201, 201):
        return

    if rotate:
        kernel = u_met.era_wind_rotate3d(kernel, date, lat, lon, level=925, ref_angle=270)
    #
    # f = plt.figure()
    # plt.imshow(kernel[0,:,:], origin='lower')


    wav_ns = np.median(kernel[:,:, 99:102], axis=2) #kernel[:,:,50] #
    # if np.sum(np.isfinite(wav_ns)) < 0.2 * wav_ns.size:
    #     return
    wav_we = np.median(kernel[:,99:102,:], axis=1) #kernel[:,50,:] #

    return wav_ns, wav_we


def file_loop(fi):

    print('Doing day: ', fi)

    date = pd.to_datetime(
        str(fi['time.year'].values) + str(fi['time.month'].values).zfill(2) + str(fi['time.day'].values).zfill(2))

    dayd = pd.Timedelta('1 days')
    if fi['time.hour'].values.size != 1:
        'hour array too big, problem!'

    if (fi['time.hour'].values) <= 16:
        print('Nighttime')
        daybefore = date - dayd
    else:
        print('Daytime')
        daybefore = date

    fdate = str(daybefore.year) + str(daybefore.month).zfill(2) + str(daybefore.day).zfill(2)

    try:
        lsta = xr.open_dataset(constants.LSTA + 'lsta_daily_' + fdate + '.nc')
    except OSError:
        return None
    print('Doing ' + 'lsta_daily_' + fdate + '.nc')

    topo = xr.open_dataset(constants.LSTA_TOPO)
    ttopo = topo['h']
    grad = np.gradient(ttopo.values)
    gradsum = abs(grad[0]) + abs(grad[1])

    lsta_da = lsta['LSTA'].squeeze()
    # f = plt.figure()
    # plt.imshow(lsta_da, origin='lower')

    if (np.sum(np.isfinite(lsta_da)) / lsta_da.size) < 0.40:
        print('Not enough valid')
        return None

    # lsta_da.values[np.isnan(lsta_da.values)] = 0
    #
    lsta_da.values[ttopo.values >= 400] = np.nan
    lsta_da.values[gradsum > 30] = np.nan
    pos = np.where((fi.values >= 5) & (fi.values < 65))

    if (np.sum(pos) == 0) | (len(pos[0]) < 3):
        print('No blobs found')
        return None

    wav_input = lsta_da.values
    points = np.where(np.isfinite(wav_input))
    inter1 = np.where(np.isnan(wav_input))
    # interpolate over sea from land points
    wav_input[inter1] = 0  #halfway between minus and plus rather than interpolate

    # try:
    #      wav_input[inter1] = griddata(points, np.ravel(wav_input[points]), inter1, method='linear')
    # except ValueError:
    #     pass
    #
    # inter = np.where(np.isnan(wav_input))
    # try:
    #      wav_input[inter] = griddata(points, np.ravel(wav_input[points]), inter, method='nearest')
    # except ValueError:
    #     wav_input[inter]=0

    wavpos = util.waveletLSTA_both(wav_input, 3)

    wlpos_dry = wavpos['power_dry']
    wlpos_wet = wavpos['power_wet']

    wlpos_dry[:,inter1[0], inter1[1]]=np.nan
    wlpos_wet[:, inter1[0], inter1[1]] = np.nan
    #wlpos[np.abs(wlpos)<3] = np.nan

    xfi = fi.shape[1]
    randx = np.random.randint(0,xfi,30)
    if np.min(pos[0]) == 0:
        ymin = np.min(pos[0])
    else:
        ymin = np.min(pos[0])-1
    if np.max(pos[0]) == fi.shape[0]-1:
        ymax = np.max(pos[0])
    else:
        ymax = np.max(pos[0])+1
    randy = np.random.randint(ymin,ymax,30)
    posr = (randy, randx)

##############################Random loop
    rnspos_list_dry = []
    rwepos_list_dry = []
    rnspos_list_wet = []
    rwepos_list_wet = []

    for y, x in zip(posr[0], posr[1]):

        lat = fi['lat'][y]
        lon = fi['lon'][x]

        point = lsta_da.sel(lat=lat, lon=lon, method='nearest')
        plat = point['lat'].values
        plon = point['lon'].values

        xpos = np.where(lsta_da['lon'].values == plon)
        xpos = int(xpos[0])
        ypos = np.where(lsta_da['lat'].values == plat)
        ypos = int(ypos[0])

        try:
            wavpos_ns, wavpos_we = cut_kernel(xpos, ypos, wlpos_dry, daybefore, plon, plat, rotate=False)
        except TypeError:
            print('Kernel random error')
            continue

        rnspos_list_dry.append(wavpos_ns)  # north-south wavelet
        rwepos_list_dry.append(wavpos_we)  # west-east wavelet

        try:
            wavpos_ns, wavpos_we = cut_kernel(xpos, ypos, wlpos_wet, daybefore, plon, plat, rotate=False)
        except TypeError:
            print('Kernel random error')
            continue

        rnspos_list_wet.append(wavpos_ns)  # north-south wavelet
        rwepos_list_wet.append(wavpos_we)  # west-east wavelet

###############################Blob loop
    nspos_list_dry = []
    wepos_list_dry = []
    nspos_list_wet = []
    wepos_list_wet = []

    for y, x in zip(pos[0], pos[1]):


        lat = fi['lat'][y]
        lon = fi['lon'][x]

        point = lsta_da.sel(lat=lat, lon=lon, method='nearest')
        plat = point['lat'].values
        plon = point['lon'].values

        xpos = np.where(lsta_da['lon'].values == plon)
        xpos = int(xpos[0])
        ypos = np.where(lsta_da['lat'].values == plat)
        ypos = int(ypos[0])


        try:
            wavpos_ns, wavpos_we = cut_kernel(xpos, ypos, wlpos_dry, daybefore, plon, plat, rotate=False)
        except TypeError:
            print('Kernel error')
            continue

        nspos_list_dry.append(wavpos_ns)  # north-south wavelet
        wepos_list_dry.append(wavpos_we)  # west-east wavelet

        try:
            wavpos_ns, wavpos_we = cut_kernel(xpos, ypos, wlpos_wet, daybefore, plon, plat, rotate=False)
        except TypeError:
            print('Kernel error')
            continue

        nspos_list_wet.append(wavpos_ns)  # north-south wavelet
        wepos_list_wet.append(wavpos_we)  # west-east wavelet


    if nspos_list_dry == []:
        print('NorthSouth empty')
        return None

    if (len(nspos_list_dry) == 1) | (len(rnspos_list_dry) == 1):
        print('NorthSouth 1')
        return None
    else:
        nspos_sum_dry = np.squeeze(np.stack(nspos_list_dry, axis=0))
        wepos_sum_dry = np.squeeze(np.stack(wepos_list_dry, axis=0))
        nspos_sum_wet = np.squeeze(np.stack(nspos_list_wet, axis=0))
        wepos_sum_wet = np.squeeze(np.stack(wepos_list_wet, axis=0))


        # nspos_sum = ((nspos_sum - np.nanmin(nspos_sum, axis=2)[..., None]) /
        #         (np.nanmax(nspos_sum, axis=2) - np.nanmin(nspos_sum, axis=2))[..., None])
        #
        # wepos_sum = ((wepos_sum - np.nanmin(wepos_sum, axis=2)[..., None]) /
        #              (np.nanmax(wepos_sum, axis=2) - np.nanmin(wepos_sum, axis=2))[..., None])

        rnspos_sum_dry = np.squeeze(np.stack(rnspos_list_dry, axis=0))
        rwepos_sum_dry = np.squeeze(np.stack(rwepos_list_dry, axis=0))
        rnspos_sum_wet = np.squeeze(np.stack(rnspos_list_wet, axis=0))
        rwepos_sum_wet = np.squeeze(np.stack(rwepos_list_wet, axis=0))

    scales = wavpos['scales']

    print('Returning')

    return (nspos_sum_dry, wepos_sum_dry,
            rnspos_sum_dry, rwepos_sum_dry,
            scales, nspos_sum_wet, wepos_sum_wet,
            rnspos_sum_wet, rwepos_sum_wet,)
# rcns_sum, rcwe_sum, cns_sum, cwe_sum,


if __name__ == "__main__":
    run_hours()
