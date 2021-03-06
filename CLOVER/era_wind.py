import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from utils import u_darrays
from utils import u_plot as up
import pdb
import salem


def slp():
    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-Int-Monthly-UVSLP.nc'


    da = xr.open_dataset(file)

    u = da['u10']
    v = da['v10']

    # ds.isel(time=ds['time.month']==8)
    u = u.isel(time=((u['time.month']>=6) & (u['time.month']<=9)))
    v = v.isel(time=((v['time.month']>=6) & (v['time.month']<=9)))

    # u = u.isel(month=(u['month']==8))
    # v = v.isel(month=(u['month']==8))


    u = u.mean(dim='time')
    v = v.mean(dim='time')

    u= u.sel(latitude=slice(20,0), longitude=slice(-20,20))
    v= v.sel(latitude=slice(20,0), longitude=slice(-20,20))

    ws  = np.sqrt(u**2+v**2)
    # uu = u[4::7, 4::7]
    # vv = v[4::7, 4::7]

    map = u.salem.get_map()

    f=plt.figure()
    ax = f.add_subplot(111)
    map.set_data(ws)

    map.visualize(ax=ax)
    qu = ax.quiver(u['longitude'].values, u['latitude'].values, u.values, v.values,
                   transform=map.transform(ax=ax), zorder=99)
    #ma# p.append_colorbar(ax=ax)

def scatter_AEJspeed_tgrad():
    srfc = '/localscratch/wllf030/cornkle/ERA-I/monthly/monthly_1979-2017_srfc.nc'
    pl = '/localscratch/wllf030/cornkle/ERA-I/monthly/monthly_1979-2017_pl.nc'


    da = xr.open_dataset(pl)
    da2 = xr.open_dataset(srfc)


    da = da['u']
    da2 = da2['t2m']

    da = da[(da['time.month'] == 5 )] #& (da['time.month'] <= 5)]
    da2 = da2[(da2['time.month'] == 5) ]#& (da2['time.month'] <= 5)]

    u = da.sel(latitude=slice(17, 5), longitude=slice(-10, 15), level=650).mean(dim='longitude')
    t2 = da2.sel(latitude=slice(17, 5), longitude=slice(-10, 15)).mean(dim='longitude')
    u850 = da.sel(latitude=slice(17, 5), longitude=slice(-10, 15), level=925).mean(dim='longitude')
    #pdb.set_trace()
    pos = np.where((u['latitude']>=4.5) & (u['latitude']<14))
    pos = pos[0]

    lat = u['latitude'].values

    print('North', u['latitude'][pos[0]:pos[0] + 4])
    print('South', u['latitude'][pos[-1] - 4:pos[-1]])

    tt = t2.values-273.15

    tgrad = tt[:, 0:-3] - tt[:, 3::]
    tgradmean = np.mean(tgrad,axis=0)

    shear = u-u850
    mshear = np.mean(shear,axis=0)

    pick = shear.sel(latitude=slice(9,7)).mean('latitude')

    plt.figure()
    plt.plot( t2['time.year'].values, pick)
    plt.title('wind shear')

    uplot = []
    tplot = []
    shearplot = []
    wwind = []

    plt.figure()
    plt.contourf( lat[0:-3], t2['time.year'].values, tgrad-tgradmean, extend='both', cmap='RdBu')
    plt.title('T2 gradient x1-x0')
    plt.colorbar()

    plt.figure()
    plt.contourf( lat, t2['time.year'].values, shear-mshear, extend='both', cmap='RdBu')
    plt.title('Wind shear x1-x0')
    plt.colorbar()

    plt.figure()
    plt.contourf( lat, t2['time.year'].values, tt, levels=np.arange(25,30,0.25), extend='both')
    plt.title('T2 in degC')
    plt.colorbar()

    plt.figure()
    plt.contourf( lat, t2['time.year'].values, u, levels=np.arange(-18,-5,1), extend='both')
    plt.title('uWind650hPa in degC')
    plt.colorbar()

    tgrads_north = np.mean((tt[:, pos])[:, 0:4], axis=1)
    tgrads_south = np.mean((tt[:, pos])[:, -3::], axis=1)

    plt.figure()
    plt.plot( t2['time.year'].values, tgrads_north-tgrads_south)

    for x in np.arange(u.shape[0]):

        usingle = u[x, :].values
        tsingle = t2[x,:].values-273.15
        u850single = u850[x, :].values
        minpos = np.argmin(usingle)
        ustrength = np.mean(usingle[minpos-1:minpos+2])
        u850strength = np.mean(u850single[minpos-1:minpos+2])

        tgrad = np.mean( tsingle[minpos-2:minpos]) - np.mean(tsingle[minpos+1:minpos+3] ) #np.mean(tsingle[pos[0]:pos[0]+4] - tsingle[pos[-1]-4:pos[-1]]))


        #print(ustrength, tgrad)

        uplot.append(ustrength)
        tplot.append(tgrad)
        shearplot.append(ustrength-u850strength)
        wwind.append(u850strength)

        if x < 2:
            plt.figure()
            plt.plot(lat[0:-1], tsingle[1::]-tsingle[0:-1], 'r')
            plt.plot(lat[0:-1], ((usingle-u850single) - np.mean(usingle-u850single))[0:-1], 'b')
            plt.plot(lat[0:-1], ((usingle) - np.mean(usingle))[0:-1], 'g')

    f = plt.figure()
    f.add_subplot(131)
    plt.scatter(tplot, uplot)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('AEJ wind speed (Mean u-wind 9-16N, 600hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')
    f.add_subplot(132)
    plt.scatter(tplot, shearplot)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('Wind shear (Mean u-wind 9-16N | 600hPa - 850hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')
    f.add_subplot(133)
    plt.scatter(tplot, wwind)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('Monsoon wind (Mean u-wind 9-16N, 850hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')



def scatter_AEJspeed_tgrad_old():
    srfc = '/localscratch/wllf030/cornkle/ERA-I/monthly/monthly_1979-2017_srfc.nc'
    pl = '/localscratch/wllf030/cornkle/ERA-I/monthly/monthly_1979-2017_pl.nc'


    da = xr.open_dataset(pl)
    da2 = xr.open_dataset(srfc)


    da = da['u']
    da2 = da2['t2m']

    da = da[(da['time.month'] == 6 )] #& (da['time.month'] <= 5)]
    da2 = da2[(da2['time.month'] == 6) ]#& (da2['time.month'] <= 5)]

    u = da.sel(latitude=slice(17, 5), longitude=slice(-10, 10), level=600).mean(dim='longitude')
    t2 = da2.sel(latitude=slice(17, 5), longitude=slice(-10, 10)).mean(dim='longitude')
    u850 = da.sel(latitude=slice(17, 5), longitude=slice(-10, 10), level=925).mean(dim='longitude')
    pos = np.where((u['latitude'] > 4.5) & (u['latitude'] < 14))
    pos = pos[0]
    print(u['latitude'][pos])

    uplot = []
    tplot = []
    shearplot = []
    wwind = []

    for x in np.arange(u.shape[0]):
        usingle = u[x, :].values
        tsingle = t2[x, :].values - 273.15
        u850single = u850[x, :].values

        ustrength = np.mean(usingle[pos])
        u850strength = np.mean(u850single[pos])
        tgrad = np.mean(np.mean(tsingle[pos[0]:pos[0] + 2] - tsingle[pos[-1] - 2:pos[-1]]))

        print(ustrength, tgrad)

        uplot.append(ustrength)
        tplot.append(tgrad)
        shearplot.append(ustrength - u850strength)
        wwind.append(u850strength)

    f = plt.figure()
    f.add_subplot(131)
    plt.scatter(tplot, uplot)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('AEJ wind speed (Mean u-wind 9-16N, 600hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')
    f.add_subplot(132)
    plt.scatter(tplot, shearplot)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('Wind shear (Mean u-wind 9-16N | 600hPa - 850hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')
    f.add_subplot(133)
    plt.scatter(tplot, wwind)
    plt.xlabel('Temperature difference (meanT[16-17N]-meanT[8-9N])')
    plt.ylabel('Monsoon wind (Mean u-wind 9-16N, 850hPa)')
    plt.title('ERA-Interim 1979-2014 [10W-10E], August')
    plt.savefig()

    f = plt.figure()






def hpa850():
    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-Int-MonthlyAvg-4D-TUVWZ.nc'


    da = xr.open_dataset(file)

    u = da['u']
    v = da['v']

    # ds.isel(time=ds['time.month']==8)
    u = u.isel(month=((u['month']>=6) & (u['month']<=9)))
    v = v.isel(month=((v['month']>=6) & (v['month']<=9)))


    u = u.mean(dim='month')
    v = v.mean(dim='month')
    print(u['level'])
    u= u.sel(level=900, latitude=slice(20,0), longitude=slice(-20,20))
    v= v.sel(level=900, latitude=slice(20,0), longitude=slice(-20,20))

    ws  = np.sqrt(u**2+v**2)
    # uu = u[4::7, 4::7]
    # vv = v[4::7, 4::7]

    map = u.salem.get_map()

    f=plt.figure()
    ax = f.add_subplot(111)
    map.set_data(ws)

    map.visualize(ax=ax)
    qu = ax.quiver(u['longitude'].values, u['latitude'].values, u.values, v.values,
                   transform=map.transform(ax=ax), zorder=99)


def itcz_trend():

    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-Int-Monthly-UVSLP.nc'

    da = xr.open_dataset(file)

    u = da['u10']
    v = da['v10']

    # ds.isel(time=ds['time.month']==8)
    u = u.sel(longitude=slice(-10,30) , latitude=slice(30,4) )
    v = v.sel(longitude=slice(-10,30) , latitude=slice(30,4) )

    itcz = v.copy()
    #iszero = itcz.where(np.abs(itcz.values) < 0.2)

    ws = np.sqrt(u ** 2 + v ** 2)

    years = np.unique(u['time.year'].values)

    dic = {}
    for m in range(1,13):

        dic[m] = []

    for ind in range(itcz.values.shape[0]):

        marr = itcz[ind]
        month = int(marr['time.month'].values)
        print(month)
        if (month <= 4) | (month >=10):
            carr = marr.copy().sel(latitude=slice(17, 4))
        else:
            carr = marr.copy()

        mean = carr.mean(dim='longitude')
        collect = []
        for c in range(carr.values.shape[1]):

            line = carr[:,c]

            pos = np.where(line >= 0.1)
            try:
                ipos = pos[0][0]
            except IndexError:
                ipos = -1

            collect.append((carr['latitude'].values)[ipos])


        #pdb.set_trace()
        laverage = np.mean(np.array(collect))
        dic[int(carr['time.month'].values)].append(laverage)


    map = u.salem.get_map()

    f = plt.figure()
    for p in np.array(range(1, 13))*25:
        ax = f.add_subplot(3,4,p/25)
        mo = p-1
        map.set_data(v[mo,:,:])
        map.set_plot_params(vmax=4, vmin=-4, cmap='RdBu')
        map.visualize(ax=ax, title=str(int(u[mo]['time.month'].values)))

        qu = ax.quiver(u['longitude'].values, u['latitude'].values, u[mo,:,:].values, v[mo,:,:].values,
                       transform=map.transform(ax=ax), zorder=99)
    f = plt.figure(figsize=(9,6))
    for p in range(1,13):

        f.add_subplot(3,4,p)
        plt.plot(years, dic[p])
        plt.title(str(int(u[p-1]['time.month'].values)))


def T2grad_trend():

    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-WA-Monthly-2mTemp.nc'

    da = xr.open_dataset(file)

    u = da['t2m']


    # ds.isel(time=ds['time.month']==8)
    u = u.sel(longitude=slice(-10,5) , latitude=slice(30,4) )


    years = np.unique(u['time.year'].values)

    dic = {}
    for m in range(1,13):

        dic[m] = []

    for ind in range(u.values.shape[0]):

        marr = u[ind]
        month = int(marr['time.month'].values)
        print(month)
        if (month <= 4) | (month >=10):
            carr = marr.copy().sel(latitude=slice(17, 4))
        else:
            carr = marr.copy()

        tgrad = carr.values
        tgrad = tgrad[2::,:] - tgrad[0:-2, :]
        lat = carr['latitude'].values[2::]

        collect = []
        for c in range(carr.values.shape[1]):

            line = tgrad[:,c]
            print(tgrad)
            pos = np.argmax(line)
            collect.append(lat[pos])


        #pdb.set_trace()
        laverage = np.mean(np.array(collect))
        dic[int(carr['time.month'].values)].append(laverage)


    #map = u[:,3::,:].salem.get_map()
    map = u.salem.get_map()

    f = plt.figure()
    for p in np.array(range(1, 13))*25:
        ax = f.add_subplot(3,4,p/25)
        mo = p-1
        bla = u[mo,:,:].values-273.15
        #tgrad = bla[3::, :] - bla[0:-3, :]
        map.set_data(bla)
        map.set_plot_params(vmax=30, vmin=26, cmap='viridis')
        map.visualize(ax=ax, title=str(int(u[mo]['time.month'].values)))

    f = plt.figure(figsize=(9,6))
    for p in range(1,13):

        f.add_subplot(3,4,p)
        plt.plot(years, dic[p])
        plt.title(str(int(u[p-1]['time.month'].values)))

def T2gradmax_trend():

    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-WA-Monthly-2mTemp.nc'

    da = xr.open_dataset(file)

    u = da['t2m']


    # ds.isel(time=ds['time.month']==8)
    u = u.sel(longitude=slice(-10,5) , latitude=slice(30,4) )


    years = np.unique(u['time.year'].values)

    dic = {}
    for m in range(1,13):

        dic[m] = []

    for ind in range(u.values.shape[0]):

        marr = u[ind]
        month = int(marr['time.month'].values)
        print(month)
        if (month <= 4) | (month >=10):
            carr = marr.copy().sel(latitude=slice(17, 4))
        else:
            carr = marr.copy()

        tgrad = carr.values
        tgrad = tgrad[2::,:] - tgrad[0:-2, :]
        lat = carr['latitude'].values[2::]

        collect = []
        for c in range(carr.values.shape[1]):

            line = tgrad[:,c]
            tgmax = np.max(line)
            collect.append(tgmax)


        #pdb.set_trace()
        print(int(carr['time.month'].values), collect)
        collect = np.array(collect)
        laverage = np.mean(collect[collect>=0.5])
        dic[int(carr['time.month'].values)].append(laverage)


    #map = u[:,3::,:].salem.get_map()
    map = u.salem.get_map()

    f = plt.figure()
    for p in np.array(range(1, 13))*25:
        ax = f.add_subplot(3,4,p/25)
        mo = p-1
        bla = u[mo,:,:].values-273.15
        #tgrad = bla[3::, :] - bla[0:-3, :]
        map.set_data(bla)
        map.set_plot_params(vmax=30, vmin=26, cmap='viridis')
        map.visualize(ax=ax, title=str(int(u[mo]['time.month'].values)))

    f = plt.figure(figsize=(9,6))
    for p in range(1,13):

        f.add_subplot(3,4,p)
        plt.plot(years, dic[p])
        plt.title(str(int(u[p-1]['time.month'].values)))


def T2NorthSouth_trend():

    file = '/localscratch/wllf030/cornkle/obs_data/ERA-I/ERA-WA-Monthly-2mTemp.nc'

    da = xr.open_dataset(file)

    u = da['t2m']


    # ds.isel(time=ds['time.month']==8)
    north = u.sel(longitude=slice(-10,10) , latitude=slice(25,20) ) # ERA is lat reversed!!!
    north2 = u.sel(longitude=slice(-10, 10), latitude=slice(15, 12))  # ERA is lat reversed!!!
    south = u.sel(longitude=slice(-10, 10), latitude=slice(8, 5.5))

    nmean = north.mean(dim=['latitude', 'longitude'])
    nmean2 = north2.mean(dim=['latitude', 'longitude'])
    smean = south.mean(dim=['latitude', 'longitude'])

    years = np.unique(u['time.year'].values)

    dic = {}
    for m in range(1,13):

        if (m <= 4) | (m >=11):
            nmm = nmean2
        else:
            nmm = nmean

        n = nmm.isel(time=((nmm['time.month'] == m)) )
        s = smean.isel(time=((smean['time.month'] == m)) )

        diff = n - s

        dic[m] = diff

    #map = u[:,3::,:].salem.get_map()
    map = u.salem.get_map()

    f = plt.figure()
    for p in np.array(range(1, 13))*25:
        ax = f.add_subplot(3,4,p/25)
        mo = p-1
        bla = u[mo,:,:].values-273.15
        #tgrad = bla[3::, :] - bla[0:-3, :]
        map.set_data(bla)
        map.set_plot_params(vmax=30, vmin=26, cmap='viridis')
        map.visualize(ax=ax, title=str(int(u[mo]['time.month'].values)))

    f = plt.figure(figsize=(9,6))
    for p in range(1,13):

        f.add_subplot(3,4,p)
        plt.plot(years, dic[p])
        plt.title(str(int(u[p-1]['time.month'].values)))


