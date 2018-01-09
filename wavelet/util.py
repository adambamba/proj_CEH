# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 14:08:18 2016

@author: cornkle
"""
import numpy as np
from wavelet import twod as w2d 
from scipy import ndimage
import pdb
def waveletTP(t, p, dt):
        
    dic= {}    
        
    #2D continuous wavelet analysis:
    #TIR   
    tir=t.copy()
    tir[tir>0] = 0
    tir = tir - np.mean(tir) 
    mother2d = w2d.Mexican_hat()
    
    powerTIR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=1./12, s0=30./mother2d.flambda(), J=45)  # s0=30./
    powerTIR[np.real(powerTIR>=0)] = 0.01
    powerTIR = (np.abs(powerTIR)) * (np.abs(powerTIR)) # Normalized wavelet power spectrum
    period2d = 1. / freqs2d    
    scales2d.shape = (len(scales2d),1,1)
    powerTIR = powerTIR / (scales2d*scales2d)
    
    #Precip
    powerPCP, scales2d, freqs2d = w2d.cwt2d(p, dt, dt, dj=1./12, s0=30./mother2d.flambda(), J=45)
    powerPCP[np.real(powerPCP<=0)] = 0.01
    powerPCP = (np.abs(powerPCP)) * (np.abs(powerPCP)) # Normalized wavelet power spectrum
    scales2d.shape = (len(scales2d),1,1)
    powerPCP = powerPCP / (scales2d*scales2d)
        
    dic['t']=powerTIR
    dic['p']=powerPCP
    dic['scales'] = (period2d/2.)
    
    return dic


def waveletT(t, dt):

    dic = {}

    # 2D continuous wavelet analysis:
    # TIR
    tir = t.copy()
    tir[tir > 0] = 0
    tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=1. / 12, s0=30. / mother2d.flambda(), J=45)  # s0=30./
    powerTIR[np.real(powerTIR >= 0)] = 0.01
    powerTIR = (np.abs(powerTIR)) * (np.abs(powerTIR))  # Normalized wavelet power spectrum
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    dic['t'] = powerTIR
    dic['scales'] = (period2d / 2.)


    return dic

def waveletT8(t, dt):

    dic = {}

    # 2D continuous wavelet analysis:
    # TIR
    tir = t.copy()
    tir[tir > 0] = 0
    tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=1. / 12, s0=40. / mother2d.flambda(), J=45)  # s0=30./
    powerTIR[np.real(powerTIR >= 0)] = 0.01
    powerTIR = (np.abs(powerTIR)) * (np.abs(powerTIR))  # Normalized wavelet power spectrum
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    dic['t'] = powerTIR
    dic['scales'] = (period2d / 2.)

    return dic

def waveletSurface(t, dt):

    dic = {}

    # 2D continuous wavelet analysis:
    # TIR
    tir = t.copy()
    tir[tir < 0] = 100
    tir[np.isnan(tir)]= 100
    #tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=0.75, s0=1500. / mother2d.flambda(), J=10)  # s0=30./
    #powerTIR[np.real(powerTIR >= 0)] = 0.01
    powerTIR = (np.abs(powerTIR)) * (np.abs(powerTIR))  # Normalized wavelet power spectrum
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    dic['power'] = powerTIR
    dic['scales'] = (period2d / 2.)

    return dic


def waveletLSTA_dom(t, dt):
    dic = {}

    # 2D continuous wavelet analysis:
    # TIR
    # dj: distance between scales
    # s0: start scale, approx 2*3*pixel scale (3 pix necessary for one wave)
    # j: number of scales

    # 2D continuous wavelet analysis:
    # TIR
    tir = t.copy()
    tir = tir
    #tir[tir < 0] = 0
    tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIRR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=0.28, s0=18. / mother2d.flambda(), J=14)  # s0=30./
    #powerTIRR[np.real(powerTIRR <= 0)] = 0

    neg = np.where(powerTIRR<0)

    powerTIR = (np.abs(powerTIRR)) * (np.abs(powerTIRR))  # Normalized wavelet power spectrum
    powerTIR[neg] = powerTIR[neg]*-1
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    maxperpix = np.argmax(powerTIR, axis=0)
    dom_scale = np.zeros_like(tir)
    scales = (period2d / 2.)
    for i in range(maxperpix.shape[0]):
        for j in range(maxperpix.shape[1]):
            max = maxperpix[i,j]
            pt = powerTIRR[:,i,j]
            ptt = powerTIR[:,i,j]
            scal = scales[max]
            ptest = pt[max]
            pttest = ptt[max]
            if ptest < 0:
                scal = scal*-1
            if pttest < 0.05:
                scal=np.nan

            dom_scale[i,j] = scal

    dic['power'] = powerTIR
    dic['scales'] = scales
    dic['dominant'] = dom_scale

    return dic


def waveletLSTA(t, dt, method=None):
    dic = {}

    # 2D continuous wavelet analysis:
    # TIR
    # dj: distance between scales
    # s0: start scale, approx 2*3*pixel scale (3 pix necessary for one wave)
    # j: number of scales

    # 2D continuous wavelet analysis:
    # TIR
    tir = t.copy()
    tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIRR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=0.28, s0=18. / mother2d.flambda(), J=14)
    if method == 'pos':
        powerTIRR[np.real(powerTIRR <= 0)] = 0.001
    if method == 'neg':
        powerTIRR[np.real(powerTIRR >= 0)] = 0.001
    isneg = np.where(powerTIRR<0)

    powerTIR = (np.abs(powerTIRR)) * (np.abs(powerTIRR))  # Normalized wavelet power spectrum
    if method == None:
        powerTIR[isneg] = powerTIR[isneg]*-1
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    dic['power'] = powerTIR
    dic['scales'] = (period2d / 2.)

    return dic


def waveletSurfaceneg(t, dt):

    dic = {}
    tir = t.copy()
    # 2D continuous wavelet analysis:
    # TIR
    tir = tir*(-1)
    tir[tir < 0] = -100
    tir[np.isnan(tir)]= -100
    #tir = tir - np.mean(tir)
    mother2d = w2d.Mexican_hat()

    powerTIR, scales2d, freqs2d = w2d.cwt2d(tir, dt, dt, dj=0.75, s0=1500. / mother2d.flambda(), J=10)  # s0=30./
    powerTIR[np.real(powerTIR <= 0)] = 0.001
    powerTIR = (np.abs(powerTIR)) * (np.abs(powerTIR))  # Normalized wavelet power spectrum
    period2d = 1. / freqs2d
    scales2d.shape = (len(scales2d), 1, 1)
    powerTIR = powerTIR / (scales2d * scales2d)

    dic['power'] = powerTIR
    dic['scales'] = (period2d / 2.)

    return dic