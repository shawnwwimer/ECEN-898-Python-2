#!/usr/bin/env python

# Canny edge detection
'''
1. Gaussian filter smoothing (done)
2. Find intensity gradient
3. Pre-massage with gradient magnitude thresholding or lower bound cut-off suppression
4. Apply double threshold to find potential edges
5. Track edge by hysteresis: finalize detection by suppressing weak edges not connected to strong edges
'''

import sys, getopt, os
import math
import numpy as np


def pad_array(img, amount, method='replication'):
    method = method
    amount = amount
    t_img = np.array(img)
    re_img = np.zeros([img.shape[0]+2*amount, img.shape[1]+2*amount])
    re_img[amount:img.shape[0]+amount, amount:img.shape[1]+amount] = t_img
    if method == 'zero':
        pass # already that way
    elif method == 'replication':
        re_img[0:amount,amount:img.shape[1]+amount] = np.flip(img[0:amount, :], axis=0) # left
        re_img[-1*amount:-1, amount:img.shape[1]+amount] = np.flip(img[-1*amount:-1, :], axis=0) # right
        re_img[:, 0:amount] = np.flip(re_img[:, amount:2*amount], axis=1) # top
        re_img[:, -1*amount:] = np.flip(re_img[:, -2*amount:-amount], axis=1) # bottom
        
    return re_img
        
def image_filter2d(img, kernel):
    # establish useful values
    imx = img.shape[0]
    imy = img.shape[1]
    kx = kernel.shape[0]
    ky = kernel.shape[1]
    if kx % 2 == 1:
        center = [math.ceil(kx/2), math.ceil(ky/2)]
    else:
        center = [int(kx/2) + 1, int(ky/2) + 1]
        
    # pad arrays and put image in center
    re_img = np.zeros([imx+2*kx, imy+2*ky])
    pad_img = np.zeros([imx+2*kx, imy+2*ky])+np.max(np.max(img))/2
    pad_img[kx:imx+kx, ky:imy+ky] = img
    
    # Perform sum of products
    for row in range(kx, imx+kx):
        for col in range(ky, imy+ky):
            for a in range(0, kx):
                for b in range(0, ky):
                    re_img[row, col] = re_img[row,col] + pad_img[row+a-center[0]+1, col+b-center[1]+1]*kernel[a,b]
    return re_img[kx:imx+kx, ky:imy+ky]

def Gaussian2D(size, sigma):
    # simplest case is where there is no Gaussian
    if size==1:
        return np.array([[0,0,0],[0,1,0],[0,0,0]])

    # parameters
    peak = 1/2/np.pi/sigma**2
    width = -2*sigma**2
    
    # Gaussian filter
    H = np.zeros([size, size])

    # populate the Gaussian
    if size % 2 == 1:
        k = (size - 1)/2
        for i in range(1, size+1):
            i_part = (i-(k+1))**2
            for j in range(1, size+1):
                H[i-1, j-1] = peak*math.exp((i_part + (j-(k+1))**2)/width)
    else:
        k = size / 2
        for i in range(1, size+1):
            i_part = (i-(k+0.5))**2
            for j in range(1, size+1):
                H[i-1, j-1] = peak*math.exp((i_part + (j-(k+0.5))**2)/width)

    # normalize the matrix
    H = H / np.sum(np.concatenate(H))
    return H