#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""jebra.py: 

"""
from __future__ import division, print_function
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import numpy as np
import cv2
import screeninfo
import time

windowName_ = 'JEBRA'
cv2.namedWindow( windowName_ )
w_, h_ = 0, 0

img_ = None

speed_ = 1000            # pixel in seconds
slitWidth_ = 100        # in pixels.

def set_resolution():
    global w_, h_
    global img_
    monitor = screeninfo.get_monitors()[-1]
    w_ = monitor.width 
    h_ = monitor.height

def init_arrays():
    global img_
    # numpy and opencv has incompatible coordinate system. So silly.
    img_ = np.zeros( (h_,w_), dtype = np.uint8 )
    for i in range( 0, h_, 2*slitWidth_ ):
        img_[:,i:i+slitWidth_] = 255

def show_frame(  waitFor = 1 ):
    global img_
    global windowName_
    cv2.imshow( windowName_, img_ )
    cv2.waitKey( waitFor )

def generate_stripes( offset = 0 ):
    global speed_, slitWidth_ 
    global img_
    offset = 5 #int( offset )
    img_ = np.roll( img_, (0,offset), axis=1)

def run( offset ):
    global img_
    global speed_, slitWidth_
    generate_stripes( offset )
    show_frame( 1 )

def main():
    set_resolution()
    init_arrays()
    t0 = time.time() 
    while True:
        dt = time.time() - t0
        t0 = time.time() 
        run( dt * speed_ )

if __name__ == '__main__':
    main()

