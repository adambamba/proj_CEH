# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:27:16 2016

@author: cornkle
"""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np
import salem
import pdb


def quick_map(xar, save = None, vmax=None, vmin=None, cmap=None, title=None):

    f = plt.figure(figsize=(10, 6), dpi=300)
    if not cmap:
        cmap='viridis'
    ax = plt.axes(projection=ccrs.PlateCarree())
    xar.plot.contourf(projection=ccrs.PlateCarree(), vmax=vmax, vmin=vmin, cmap=cmap)
    ax.coastlines()
    # Gridlines
    xl = ax.gridlines(draw_labels=True);
    xl.xlabels_top = False
    xl.ylabels_right = False
    # Countries
    ax.add_feature(cartopy.feature.BORDERS, linestyle='--');
    plt.title(title)
    if save:
        plt.savefig(save)
    else:
        plt.show()

def quick_map_salem(xar, save = None, vmax=None, vmin=None, cmap=None, title=None):

    map = xar.salem.get_map(cmap='viridis')
    map.set_shapefile(rivers=True)

    map.set_plot_params()

    map.set_data(xar, interp='linear')
    map.visualize()

    f = plt.figure(figsize=(10, 6), dpi=300)

    plt.title(title)
    if save:
        plt.savefig(save)
    else:
        plt.show()

def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)

    #return base.from_list(cmap_name, color_list, N)
    return plt.cm.get_cmap(base_cmap, N)