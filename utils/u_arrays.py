# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:27:16 2016

@author: cornkle
"""

import os
import numpy as np
from scipy.ndimage.measurements import label
from utils import u_mann_kendall as mk


def locate(pattern, root_path, exclude=None):
    strg = []
    llist = os.listdir(root_path)
    llist.sort()
    for file in llist:
        if file.endswith(pattern):
            filepath = os.path.join(root_path, file)

            try:
                if exclude in filepath:
                    continue
            except TypeError:
                pass
            strg.append(os.path.join(root_path, file))
    return strg



def distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) *(x1 - x2) + (y1 - y2) * (y1 - y2))


def closest_point(point, points):
    dist_2 = np.sum((points - point) * (points - point), axis=1)
    return np.argmin(dist_2)


"""create one unique integer from two positive integers
 Cantor pairing function"""
def unique_of_pair(x,y):

    uni = (x + y) * (x + y + 1) / 2 + y
    return uni


"""
Find all indices within the local circle of radius
Input:
x: x index of center point
y: y index of center point
radius: radius in pixels, floats are handled including the farthest point
Returns a tuple of (y index, x index)
"""
def draw_circle(x, y, radius):

    xloc1 = np.arange(x - radius, x + radius + 1)
    yloc1 = np.arange(y - radius, y + radius + 1)
    xloc, yloc = np.meshgrid(xloc1, yloc1)
    distloc = ( ((xloc - x) * (xloc - x)) + ((yloc - y) * (yloc - y)) )**.5

    indloc = (distloc <= radius).nonzero()
    ycirc = indloc[0] - radius + y
    xcirc = indloc[1] - radius + x

    return (ycirc, xcirc)


"""
Find all indices within the local circle of radius
Input:
x: x index of center point
y: y index of center point
radius: radius in pixels, floats are handled including the farthest point
Returns a tuple of (y index, x index)
"""
def draw_ellipse(x, y, short, long):


    xloc = np.arange(x-np.round(short), x+np.round(short)+1)
    yloc = np.arange(y-np.round(long), y+np.round(long)+1)[:,None]
    #xloc, yloc = np.meshgrid(xloc1, yloc1)
    distloc = ((xloc - x)/short)**2 + ((yloc - y)/long)**2 <=1

    pos = np.where(distloc)

    ycirc = pos[0]+y
    xcirc = pos[1]+x

    return (ycirc, xcirc)


"""
Find all indices within the local circle of radius but remove indeces that
are out of an area box, specified with an 2d array.
Input:
x: x index of center point
y: y index of center point
radius: radius in pixels, floats are handled including the farthest point
Returns a tuple of (y index, x index)
"""
def draw_cut_circle(x, y, radius, array):

    ycirc, xcirc = draw_circle(x, y, radius)
    noky = np.where(ycirc >= array.shape[0])  # if the circle is off the edge
    if noky[0].size > 0:
        ycirc = np.delete(ycirc, noky)
        xcirc = np.delete(xcirc, noky)

    nokx = np.where(xcirc >= array.shape[1])
    if nokx[0].size > 0:
        ycirc = np.delete(ycirc, nokx)
        xcirc = np.delete(xcirc, nokx)

    return (ycirc, xcirc)


"""
Find all indices creating the ring of a local circle of radius but remove indeces that
are out of an area box, specified with an 2d array.
Input:
x: x index of center point
y: y index of center point
radius: radius in pixels, floats are handled including the farthest point
Returns a tuple of (y index, x index)
"""
def draw_ring(x, y, inrad, outrad, array):

    in_ycirc, in_xcirc = draw_cut_circle(x, y, inrad, array)
    out_ycirc, out_xcirc = draw_cut_circle(x, y, outrad, array)

    in_uni=unique_of_pair(in_xcirc, in_ycirc)
    out_uni = unique_of_pair(out_xcirc, out_ycirc)

    inter = np.in1d(out_uni, in_uni, assume_unique=True)

    if np.sum(inter) != 0:
        nok = np.where(inter)
        out_ycirc = np.delete(out_ycirc, nok)
        out_xcirc = np.delete(out_xcirc, nok)

    return (out_ycirc, out_xcirc)


def cut_kernel(array, xpos, ypos, dist_from_point):
    """
     This function cuts out a kernel from an existing array and allows the kernel to exceed the edges of the input
     array. The cut-out area is shifted accordingly within the kernel window with NaNs filled in
    :param array: 2darray
    :param xpos: middle x point of kernel
    :param ypos: middle y point of kernel
    :param dist_from_point: distance to kernel edge to each side
    :return: 2d array of the chosen kernel size.
    """

    if array.ndim != 2:
        raise IndexError('Cut kernel only allows 2D arrays.')

    kernel = np.zeros((dist_from_point*2+1, dist_from_point*2+1)) * np.nan

    if xpos - dist_from_point >= 0:
        xmin = 0
        xmindist = dist_from_point
    else:
        xmin = (xpos - dist_from_point) * -1
        xmindist = dist_from_point + (xpos - dist_from_point)

    if ypos - dist_from_point >= 0:
        ymin = 0
        ymindist = dist_from_point
    else:
        ymin = (ypos - dist_from_point) * -1
        ymindist = dist_from_point + (ypos - dist_from_point)

    if xpos + dist_from_point < array.shape[1]:
        xmax = kernel.shape[1]
        xmaxdist = dist_from_point + 1
    else:
        xmax = dist_from_point - (xpos - array.shape[1])
        xmaxdist = dist_from_point - (xpos + dist_from_point - array.shape[1])

    if ypos + dist_from_point < array.shape[0]:
        ymax = kernel.shape[0]
        ymaxdist = dist_from_point + 1
    else:
        ymax = dist_from_point - (ypos - array.shape[0])
        ymaxdist = dist_from_point - (ypos + dist_from_point - array.shape[0])

    cutk = array[ypos - ymindist: ypos + ymaxdist, xpos - xmindist: xpos + xmaxdist]


    kernel[ymin: ymax, xmin:xmax] = cutk

    return kernel

def cut_kernel_3d(array, xpos, ypos, dist_from_point):
    """
     This function cuts out a kernel from an existing array and allows the kernel to exceed the edges of the input
     array. The cut-out area is shifted accordingly within the kernel window with NaNs filled in
    :param array: 2darray
    :param xpos: middle x point of kernel
    :param ypos: middle y point of kernel
    :param dist_from_point: distance to kernel edge to each side
    :return: 2d array of the chosen kernel size.
    """

    if array.ndim != 3:
        raise IndexError('Cut kernel3d only allows 3D arrays.')

    kernel = np.zeros((array.shape[0], dist_from_point*2+1, dist_from_point*2+1)) * np.nan

    if xpos - dist_from_point >= 0:
        xmin = 0
        xmindist = dist_from_point
    else:
        xmin = (xpos - dist_from_point) * -1
        xmindist = dist_from_point + (xpos - dist_from_point)

    if ypos - dist_from_point >= 0:
        ymin = 0
        ymindist = dist_from_point
    else:
        ymin = (ypos - dist_from_point) * -1
        ymindist = dist_from_point + (ypos - dist_from_point)

    if xpos + dist_from_point < array.shape[2]:
        xmax = kernel.shape[2]
        xmaxdist = dist_from_point + 1
    else:
        xmax = dist_from_point - (xpos - array.shape[2])
        xmaxdist = dist_from_point - (xpos + dist_from_point - array.shape[2])

    if ypos + dist_from_point < array.shape[1]:
        ymax = kernel.shape[1]
        ymaxdist = dist_from_point + 1
    else:
        ymax = dist_from_point - (ypos - array.shape[1])
        ymaxdist = dist_from_point - (ypos + dist_from_point - array.shape[1])

    cutk = array[:, ypos - ymindist: ypos + ymaxdist, xpos - xmindist: xpos + xmaxdist]


    kernel[:, ymin: ymax, xmin:xmax] = cutk

    return kernel



def blob_define(array, thresh, min_area=None, max_area=None, minmax_area=None):
    array[array >= thresh] = 0  # T threshold maskout
    array[np.isnan(array)] = 0  # set ocean nans to 0

    labels, numL = label(array)

    u, inv = np.unique(labels, return_inverse=True)
    n = np.bincount(inv)

    goodinds = u[u!=0]

    if min_area != None:
        goodinds = u[(n>=min_area) & (u!=0)]
        badinds = u[n<min_area]

        for b in badinds:
            pos = np.where(labels==b)
            labels[pos]=0

    if max_area != None:
        goodinds = u[(n<=max_area)  & (u!=0)]
        badinds = u[n>max_area]

    if minmax_area != None:
        goodinds = u[(n <= minmax_area[1]) & (u != 0) & (n>=minmax_area[0])]
        badinds = u[(n > minmax_area[1]) | (n < minmax_area[0])]

        for b in badinds:
            pos = np.where(labels==b)
            labels[pos]=0

    return labels, goodinds



def linear_trend(x, eps=0.001, alpha=0.01):

    #pf = np.polyfit(np.arange(len(x)), x, 1)
    pf, slope, int, p, ind = mk.test(np.arange(len(x)),x.squeeze().values, eps=eps, alpha=alpha, Ha='upordown')

    # we need to return a dataarray or else xarray's groupby won't be happy

    if ind == 1:
        issig = slope
    else:
        issig = np.nan

    return issig








