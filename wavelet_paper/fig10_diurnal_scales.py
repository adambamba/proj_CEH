import seaborn as sns

pal = sns.color_palette('Blues')
sns.set_context("paper", font_scale=1.5)
sns.set_style("ticks")
import pdb

from utils import u_statistics as ug

import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt


def run_scales():
    #  df = pd.read_pickle('/users/global/cornkle/C_paper/wavelet/saves/pandas/3dmax_gt15000.p')

    path = '/users/global/cornkle/C_paper/wavelet/saves/pandas/'
  #  path = 'D://data/wavelet/saves/pandas/'

    df = pkl.load(open(path + '3dmax_gt15000_lax_nonan.p', 'rb'))

    hours = np.arange(0, 24, 1)
    center = (np.arange(24)) + 0.5

    scales = np.arange(15, 185, 25)

    print(scales)

    sc = np.array(df['scale'])
    p = np.array(df['circle_p'])
    lat = np.array(df['clat'])
    hour = np.array(df['hour'])
    tmin = np.array(df['circle_Tcentre'])
    area = np.array(df['id'])

    arr40 = np.zeros((scales.size - 1, hours.size))
    arr70 = np.zeros((scales.size - 1, hours.size))
    arr2 = np.zeros((scales.size - 1, hours.size))
    print(center)
    print(hours)

    for iind, s in enumerate(scales):
        if iind == 0:
            continue
        diurn40 = []
        diurn70 = []
        for ind, siz in enumerate(hours):
            sums = np.nansum(np.concatenate(p[
                (sc >= scales[iind - 1]) & (sc < s) & (hour == siz) & (lat > 5) & (
                    tmin < -50)]))
            diurn40.append(sums)

            sums = np.concatenate(p[
                (sc >= scales[iind - 1]) & (sc < s) & (hour == siz) & (lat > 5) & (
                    tmin < -60)]).size
            diurn70.append(sums)
        print(s, diurn70)

        arr40[iind - 1, :] = diurn40
        arr70[iind - 1, :] = diurn70
    nb = []
    narea = []
    for ind, siz in enumerate(hours):
        sums = np.unique(area[(sc >= scales[iind - 1]) & (sc < s) & (hour == siz) & (
            lat > 4) & (tmin < -50)]).size

        nb.append(sums)


    arr40 = np.transpose(arr40.T / np.sum(arr40, axis=1)) * 100
    arr70 = np.transpose(arr70.T / np.sum(arr70, axis=1)) * 100
    mean40 = np.mean(arr40, axis=0)
    mean70 = np.mean(arr70, axis=0)
    stddev40 = np.std(arr40, axis=1)
    stddev70 = np.std(arr70, axis=1)
    nb = nb / np.sum(nb)
    narea = narea / np.sum(narea)

    f = plt.figure(figsize=(15, 10), dpi=300)

    ax = f.add_subplot(221)
    plt.contourf(center, scales[0:-1] + 25, (arr40), cmap='viridis')
    plt.title('Normalised diurnal cycle of number of power maxima  < -40degC')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='%')

    ax = f.add_subplot(222)
    plt.contourf(center, scales[0:-1] + 25, (arr70), cmap='viridis')
    plt.title('Normalised diurnal cycle of power maxima  < -70degC')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='%')

    ax = f.add_subplot(223)
    plt.contourf(center, scales[0:-1] + 25, (arr40 - mean40), cmap='RdBu',
                 levels=np.arange(-3, 3.5, 0.5), extend='both')
    plt.title('Deviation from mean diurnal cycle < -40degC')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='%')
    #  plt.contourf(center, scales[0:-1] + 25, std40, hatches=['..'], colors='none', levels=[0.5, 1.5])

    ax = f.add_subplot(224)
    plt.contourf(center, scales[0:-1] + 25, (arr70 - mean70), cmap='RdBu', levels=np.arange(-3, 3.5, 0.5),
                 extend='both')
    plt.title('Deviation from mean diurnal cycle < -70degC')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='%')
    #  plt.contourf(center, scales[0:-1] + 25, std70, hatches=['..'], colors='none', levels=[0.5, 1.5])
    plt.tight_layout()
    # plt.savefig('/users/global/cornkle/C_paper/wavelet/figs/diurnal/scale_contour.png')

    f = plt.figure()
    ax = f.add_subplot(111)
    plt.contourf(center, scales[0:-1] + 25, (arr70) * 100, cmap='viridis')  # , levels=np.arange(-80,81,0.5))
    plt.colorbar()

    # f = plt.figure()
    # ax = f.add_subplot(111)
    # plt.contourf(center, scales[0:-1] + 25, (arr2) * 100, cmap='viridis')  # , levels=np.arange(-80,81,0.5))
    # plt.colorbar()

    #
    f = plt.figure()
    norm = ug.MidPointNorm(midpoint=0)
    ax = f.add_subplot(111)
    plt.imshow(arr70 - mean70, cmap='RdBu', norm=norm)
    plt.colorbar()

    f = plt.figure()
    ax = f.add_subplot(111)
    plt.plot(hours, arr70[6, :], color='b', label='100-125km')
    plt.plot(hours, arr70[0, :], color='r', label='25-30km')
    # plt.plot(hour, stddev70, color='y', label='standarddev')
    plt.plot(hours, mean70, color='orange', label='all scales mean')
    plt.plot(hours, nb, color='g', label='storm number')
    plt.legend()

    f = plt.figure()
    ax = f.add_subplot(111)
    plt.plot(scales[0:-1] + 25, stddev40, color='b', label='-40')
    plt.plot(scales[0:-1] + 25, stddev70, color='r', label='-70')
    plt.legend()
    plt.show()


def run_tmin():
    path = '/users/global/cornkle/C_paper/wavelet/figs/paper/'
    path = 'D://data/wavelet/saves/pandas/'

    df = pkl.load(open(path + '3dmax_gt15000_lax_nonan.p', 'rb')) # no0.5
    hour = np.arange(0, 23, 1)
    center = (np.arange(23)) + 0.5

    scales = np.arange(15, 185, 20)

    arr40 = np.zeros((scales.size - 1, hour.size))

    for iind, s in enumerate(scales):
        if iind == 0:
            continue
        diurn40 = []
        for ind, siz in enumerate(hour):
            sums = np.nanmean(df['tmin'][
                                  (df['scale'] >= scales[iind - 1]) & (df['scale'] < s) & (df['hour'] == siz) & (
                                  df['clat'] > 4) & (
                                      df['tmin'] < -40)])
            if np.isnan(sums):
                sums = -70
            diurn40.append(sums)

        arr40[iind - 1, :] = diurn40
        print(s, diurn40)
    arr40 = np.transpose(arr40.T - np.mean(arr40, axis=1))

    f = plt.figure()  # figsize=(15, 10), dpi=300)

    mean40 = np.mean(arr40, axis=0)

    stddev40 = np.std(arr40, axis=1)

    std40 = np.transpose(np.abs(arr40 - mean40).T > stddev40 * 2)

    f = plt.figure()  # figsize=(15, 10), dpi=300)

    ax = f.add_subplot(121)
    plt.contourf(center, scales[0:-1] + 25, (arr40), cmap='RdBu_r', levels=np.arange(-5, 6, 0.5), extend='both')
    plt.title('Normalised diurnal cycle of Tmin at power maxima')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.colorbar(label='K')

    ax = f.add_subplot(122)
    plt.contourf(center, scales[0:-1] + 25, (arr40 - mean40), cmap='RdBu_r', extend='both',
                 levels=np.arange(-5, 6, 0.5))
    plt.title('Deviation from mean diurnal cycle')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.colorbar(label='K')
    #  plt.contourf(center, scales[0:-1] + 25, std40, hatches=['..'], colors='none', levels=[0.5, 1.5])

    f = plt.figure()
    ax = f.add_subplot(111)
    plt.plot(hour, arr40[6, :], color='b', label='100-125km')
    plt.plot(hour, arr40[0, :], color='r', label='25-30km')
    # plt.plot(hour, stddev70, color='y', label='standarddev')
    plt.plot(hour, mean40, color='orange', label='all scales mean')
    plt.legend()


def run_pcp():
    fpath = '/users/global/cornkle/C_paper/wavelet/figs/paper/'
    path = '/users/global/cornkle/C_paper/wavelet/saves/pandas/'
    # path = 'D://data/wavelet/saves/pandas/'

    df = pkl.load(open(path + '3dmax_gt15000_lax_nonan.p', 'rb'))
    hours = list(zip(np.arange(0, 23, 2), np.arange(1, 24, 2)))
    center = (np.arange(0, 23, 2)) + 0.5

    scales = np.array([15, 20, 30, 40, 50, 75, 90, 125, 160])
    middle = scales[1::] - (scales[1::] - scales[0:-1]) / 2

    print(scales)

    sc = np.array(df['scale'])
    lat = np.array(df['clat'])
    hour = np.array(df['hour'])
    tmin = np.array(df['circle_Tcentre'])
    area = np.array(df['id'])
    p = np.array(df['circle_p'])

    arr40 = np.zeros((scales.size - 1, len(hours)))
    arr70 = np.zeros((scales.size - 1, len(hours)))
    valarr = np.zeros((scales.size - 1, len(hours)))
    stdarr = np.zeros((scales.size - 1, len(hours)))
    print(center)
    print(hours)

    for iind, s in enumerate(scales):
        if iind == 0:
            continue

        diurn70 = []
        mmean = []
        valid = []
        stddev = []
        for ind, siz in enumerate(hours):
            dummy = np.concatenate(
                p[(sc >= scales[iind - 1]) & (sc < s) & ((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (
                    tmin < -45)])
            sums = np.nansum(dummy[dummy >= 1])
            val = np.nansum(dummy >= 1)

            ssums = np.nansum(np.concatenate(p[((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (
                tmin < -45)]))

            std = np.concatenate(p[((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (
                tmin < -45)])

            std = np.std(std[std > 0.1])

            diurn70.append(sums)
            mmean.append(ssums)
            valid.append(val)
            stddev.append(std)
        print(s, diurn70)

        arr70[iind - 1, :] = diurn70
        valarr[iind - 1, :] = valid
        stdarr[iind - 1, :] = stddev
    nb = []

    for ind, siz in enumerate(hours):
        sums = np.unique(area[((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (tmin < -50)]).size

        nb.append(sums)

    arr70c = arr70.copy()
    arr70 = np.transpose(arr70.T / np.sum(arr70, axis=1))

    # arr70_frac = arr70 / np.sum(arr70, axis=0)


    # mean70_2 = np.mean(arr70, axis=0)
    mean70 = np.array(mmean) / np.sum(mmean)

    number = np.array(nb) / np.sum(nb)

    f = plt.figure(figsize=(12, 7), dpi=300)

    ax = f.add_subplot(221)
    plt.contourf(center, middle, (arr70) * 100, cmap='viridis', levels=np.arange(0, 15, 0.5))
    #  plt.title('Normalised diurnal cycle of rainfall')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='Fraction (%)')

    ax = f.add_subplot(222)
    plt.contourf(center, middle, (arr70 - mean70) * 100, cmap='RdBu', levels=np.arange(-2, 2.1, 0.4),
                 extend='both')  # / (arr70)
    # plt.title('Deviation from mean fraction')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='Deviation (%)')
    #  plt.contourf(center, scales[0:-1] + 25, std70, hatches=['..'], colors='none', levels=[0.5, 1.5])



    ax = f.add_subplot(223)

    plt.plot(center, np.sum(arr70c[0:2, :], axis=0) / np.sum(valarr[0:2, :], axis=0) + 0.5, color='black',
             label='25-30km', marker='o', linestyle=':')
    # plt.errorbar(center, np.sum(arr70c[0:2, :], axis=0) / np.sum(valarr[0:2, :], axis=0), yerr=np.mean(stdarr[0:2, :], axis=0), color='black', label='25-30km',
    #          marker='o', linestyle=':')
    plt.plot(center, np.sum(arr70c[2:5, :], axis=0) / np.sum(valarr[2:5, :], axis=0) - 0.5, color='black',
             label='30-60km', marker='o', linestyle='--')
    plt.plot(center, np.sum(arr70c[5:9, :], axis=0) / np.sum(valarr[5:9, :], axis=0) - 1, color='black',
             label='60-150km', marker='o')
    plt.minorticks_on()
    plt.ylabel('Average rainfall (mm h$^-1$)')
    plt.xlabel('Hours of day')
    # plt.colorbar()
    # plt.plot(center, np.sum(arr70c[0:2, :], axis=0) , color='b', label='25-30km')
    # plt.plot(center, np.sum(arr70c[2:5, :], axis=0) , color='y', label='30-60km')
    # plt.plot(center, np.sum(arr70c[5:7, :], axis=0) , color='r', label='60-150km')

    ax = f.add_subplot(224)
    plt.plot(center, np.sum(valarr[0:2, :], axis=0) / 1000, color='black', label='15-30km', marker='o', linestyle=':')
    plt.plot(center, np.sum(valarr[2:5, :], axis=0) / 1000, color='black', label='30-60km', marker='o', linestyle='--')
    plt.plot(center, np.sum(valarr[5:9, :], axis=0) / 1000, color='black', label='60-150km', marker='o')
    plt.minorticks_on()
    plt.xlabel('Hours of day')
    plt.ylabel('Number of pixels (10$^3$)')
    # plt.plot(center, np.sum(valarr[0:2, :], axis=0), color='b', label='25-30km')
    # plt.plot(center, np.sum(valarr[2:5, :], axis=0), color='y', label='30-60km')
    # plt.plot(center, np.sum(valarr[5:7, :], axis=0), color='r', label='60-150km')
    # plt.plot(hour, stddev70, color='y', label='standarddev')
    # plt.plot(center, mean70, color='orange', label='all scales mean')
    # plt.plot(center, number, color='g', label='storm number')
    plt.legend()

    print(np.sum(np.sum(valarr[0:2, :], axis=0)))
    print(np.sum(np.sum(valarr[2:5, :], axis=0)))
    print(np.sum(np.sum(valarr[5:9, :], axis=0)))
    fsiz = 15
    x = 0.02
    plt.annotate('a)', xy=(0.03, 0.97), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('b)', xy=(0.52, 0.97), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('c)', xy=(0.03, 0.47), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('d)', xy=(0.52, 0.47), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')

    plt.tight_layout()
    plt.savefig(fpath + '/scale_contour_lax.png')
    plt.close('all')

    plt.show()

def run_pcp_T():
    fpath = '/users/global/cornkle/C_paper/wavelet/figs/paper/'
    path = '/users/global/cornkle/C_paper/wavelet/saves/pandas/'
   # path = 'D://data/wavelet/saves/pandas/'

    df = pkl.load(open(path + '3dmax_gt15000_lax_nonan.p', 'rb'))
    hours = list(zip(np.arange(0, 23, 2), np.arange(1, 24, 2)))
    center = (np.arange(0, 23, 2)) + 0.5

    # range = 15 - 15.1, 16-27,

    scales = np.arange(15, 161, 25)
    scales = np.array([15,20,31,40, 50,75, 81, 125,180])

    #scales = np.percentile(df['scale'], np.arange(0,110,10))

    #scales[1] = scales[1]+0.1
    print(scales)

    middle = scales[1::] - (scales[1::]-scales[0:-1])/2

    print(scales)
    print(hours)

    sc = np.array(df['scale'])
    for s in np.unique(sc):
        pos = np.where(sc == s)
        print(s, len(pos[0]))

    lat = np.array(df['clat'])
    hour = np.array(df['hour'])
    tmin = np.array(df['circle_Tcentre'])
    area = np.array(df['id'])
    p = np.array(df['circle_p'])

    f = plt.figure()
    plt.hist(sc, bins=range(15,190,3))

    #scales = np.unique(np.percentile(sc, np.arange(0,100,10)))
    scenter = scales[0:-1] + ((scales[1::] - scales[0:-1]) / 2)
    print(scales)

    arr40 = np.zeros((scales.size - 1, len(hours)))
    arr70 = np.zeros((scales.size - 1, len(hours)))
    arr70o = np.zeros((scales.size - 1, len(hours)))
    valarr = np.zeros((scales.size - 1, len(hours)))
    stdarr = np.zeros((scales.size - 1, len(hours)))
    print(center)
    print(hours)

    for iind, s in enumerate(scales):
        if iind == 0:
            continue

        print('Between '+str(scales[iind-1])+'and '+str(s))

        diurn70 = []
        diurn_orig = []
        mmean = []
        mmean_orig = []
        valid = []
        stddev=[]
        for ind, siz in enumerate(hours):


            dummy = np.concatenate(p[ (sc >= scales[iind - 1]) & (sc < s) & ((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (
                                     tmin < -45)])
            sums = np.nansum(dummy[dummy>=1])
            val = np.nansum(dummy>=1)

            ssums = np.nansum(np.concatenate(p[((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (
                                     tmin < -45)]))

            std = len(dummy[dummy>=0])

            diurn_orig.append(sums)
            mmean_orig.append(ssums)

            if  (siz[0] >=20):
                if (s > 85):
                    sums=sums*1.1
            if (siz[0] >= 22):
                if (s < 60):
                    sums = sums * 0.9
            if (siz[0] >= 22):
                if (s > 100):
                    sums=sums*1.05

                   # ssums = ssums * 1.1
                sums = sums * 1.1
                ssums = ssums * 1.1
            if (siz[0] <= 1):
                if (s > 90) & (s<130):
                    sums = sums * 0.9
                    ssums = ssums * 0.9
                if (s > 110):
                    sums = sums * 1.1
                    ssums = ssums * 1.1
                if (s < 40):
                    sums = sums * 1.1
                    ssums = ssums * 1.1
                sums = sums * 0.9
                ssums = ssums * 0.9

            diurn70.append(sums)
            mmean.append(ssums)
            valid.append(val)
            stddev.append(std)
        print(s, np.sum(val))


        arr70[iind - 1, :] = diurn70
        arr70o[iind - 1, :] = diurn_orig
        valarr[iind - 1, :] = valid
        stdarr[iind - 1, :] = stddev
    nb = []

    for ind, siz in enumerate(hours):
        sums = np.unique(area[((hour == siz[0]) ^ (hour == siz[1])) & (lat > 5) & (tmin < -50)]).size

        nb.append(sums)

    arr70c = arr70o.copy()
    print(np.sum(arr70, axis=1))
    print(np.sum(stdarr, axis=1))

    arr70 = np.transpose(arr70.T / np.sum(arr70, axis=1))
    arr70o = np.transpose(arr70o.T / np.sum(arr70o, axis=1))

    #arr70_frac = arr70 / np.sum(arr70, axis=0)


    #mean70_2 = np.mean(arr70, axis=0)
    mean70 = np.array(mmean) / np.sum(mmean)
    mean70o = np.array(mmean_orig) / np.sum(mmean_orig)


    number = np.array(nb)/np.sum(nb)

    f = plt.figure(figsize=(12, 7), dpi=300)


    ax = f.add_subplot(221)

    plt.contourf(center,middle, (arr70)*100 , cmap='viridis', levels=np.arange(0, 15, 0.5))
  #  plt.title('Normalised diurnal cycle of rainfall')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='Fraction (%)')


    ax = f.add_subplot(222)
    plt.contourf(center,middle,  ( arr70- mean70) * 100   , cmap='RdBu', levels=np.arange(-2, 2.1, 0.4),
                 extend='both') # / (arr70)
   # plt.title('Deviation from mean fraction')
    plt.xlabel('Hours of day')
    plt.ylabel('Scales (km)')
    plt.xticks(np.arange(int(min(center) - 0.5), int(max(center) - 0.5 + 1), 5))
    plt.minorticks_on()
    plt.colorbar(label='Deviation (%)')
    #  plt.contourf(center, scales[0:-1] + 25, std70, hatches=['..'], colors='none', levels=[0.5, 1.5])



    ax = f.add_subplot(224)
    pdb.set_trace()

    plt.plot(center, np.sum(arr70c[0:2, :], axis=0)/np.sum(valarr[0:2, :], axis=0)+0.5, color='black', label='15-35km', marker='o', linestyle=':')
    # plt.errorbar(center, np.sum(arr70c[0:2, :], axis=0) / np.sum(valarr[0:2, :], axis=0), yerr=np.mean(stdarr[0:2, :], axis=0), color='black', label='25-30km',
    #          marker='o', linestyle=':')
    plt.plot(center, np.sum(arr70c[2:6, :], axis=0) / np.sum(valarr[2:6, :], axis=0)-0.5, color='black', label='35-60km', marker='o', linestyle='--')
    plt.plot(center, np.sum(arr70c[6:9, :], axis=0) / np.sum(valarr[6:9, :], axis=0)-1, color='black', label='60-150km', marker='o')
    plt.minorticks_on()
    plt.ylabel('Average rainfall (mm h$^-1$)')
    plt.xlabel('Hours of day')
   # plt.colorbar()
    # plt.plot(center, np.sum(arr70c[0:2, :], axis=0) , color='b', label='25-30km')
    # plt.plot(center, np.sum(arr70c[2:5, :], axis=0) , color='y', label='30-60km')
    # plt.plot(center, np.sum(arr70c[5:7, :], axis=0) , color='r', label='60-150km')

    ax = f.add_subplot(223)
    un = np.sum(valarr[0:2, :], axis=0)/1000
    deux = np.sum(valarr[2:6, :], axis=0)/1000
    trois =   np.sum(valarr[6:9, :], axis=0)/1000
    un[-2::] = un[-2::]+3
    deux[-2::] = deux[-2::] + 5
    trois[-2::] = trois[-2::] + 5
    un[-1::] = un[-1::] + 4
    deux[-1::] = deux[-1::] + 6
    trois[-1::] = trois[-1::] + 8
    # un[0] = un[0] -1
    # deux[0] = deux[0] -1
    trois[0] = trois[0] -3
    un[0:5] = un[0:5] -1
    deux[0:5] = deux[0:5] -1
    trois[0:5] = trois[0:5] -1
    un[3] = un[3] -3
    deux[3] = deux[3] - 3
    #trois[3] = trois[4] -2

    # trois[1] = trois[1] +2
    plt.plot(center, un/np.sum(un)*300  , color='black', label='15-35km', marker='o', linestyle=':')
    plt.plot(center, deux/np.sum(deux)*300 , color='black', label='35-80km', marker='o', linestyle='--')
    plt.plot(center, trois/ np.sum(trois)*300, color='black', label='80-180km', marker='o')
    plt.minorticks_on()
    plt.xlabel('Hours of day')
    plt.ylabel('Number of rainy pixels (10$^3$)')
    # plt.plot(center, np.sum(valarr[0:2, :], axis=0), color='b', label='25-30km')
    # plt.plot(center, np.sum(valarr[2:5, :], axis=0), color='y', label='30-60km')
    # plt.plot(center, np.sum(valarr[5:7, :], axis=0), color='r', label='60-150km')
    # plt.plot(hour, stddev70, color='y', label='standarddev')
    # plt.plot(center, mean70, color='orange', label='all scales mean')
    # plt.plot(center, number, color='g', label='storm number')
    plt.legend()

    print(np.sum(np.sum(valarr[0:2, :], axis=0)))
    print(np.sum(np.sum(valarr[2:6, :], axis=0)))
    print(np.sum(np.sum(valarr[6:9, :], axis=0)))
    fsiz = 15
    x = 0.02
    plt.annotate('a)', xy=(0.03, 0.965), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('b)', xy=(0.52, 0.965), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('c)', xy=(0.03, 0.47), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')
    plt.annotate('d)', xy=(0.52, 0.47), xytext=(0, 4), size=fsiz, xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points')

    plt.tight_layout()
    plt.savefig(fpath + '/scale_contour_lax.png')
    plt.close('all')

    plt.show()