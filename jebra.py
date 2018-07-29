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
import screeninfo
import time
import gi
import signal

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

from PIL import Image, ImageTk

w_, h_     = 0, 0
img_       = None
tkImage_   = None
speed_     = 100            # pixel in seconds
slitWidth_ = 100        # in pixels.
t_         = time.time()
root_      = tk.Tk()
label_     = None

def set_resolution():
    global w_, h_
    global img_
    monitor = screeninfo.get_monitors()[-1]
    w_ = monitor.width  // 2
    h_ = monitor.height // 2
    # make sure that width is divisible by slitWidth_ and must be even.
    #  nSlits = w_ // slitWidth_
    #  nSlits = nSlits - (nSlits % 2 ) + 1
    #  w_ = nSlits * slitWidth_

def init_arrays():
    global img_
    global im_, tkImage_
    # numpy and opencv has incompatible coordinate system. So silly.
    print( 'I', end = '' )
    sys.stdout.flush()
    img_ = np.dstack([np.zeros( (h_, w_), dtype = np.uint8) for i in range(3)])
    print( img_.shape )
    for i in range( 0, w_, 2*slitWidth_ ):
        img_[:,i:i+slitWidth_,:] = 255

    im = Image.fromarray( img_ )
    im.save( "__background.png" )
    tkImage_   = ImageTk.PhotoImage( im )

def show_frame(  waitFor = 1 ):
    global img_
    global windowName_
    cv2.imshow( windowName_, img_ )
    cv2.waitKey( waitFor )

def generate_stripes( offset = 0 ):
    global speed_, slitWidth_ 
    global tkImage_, label_
    global img_

    offset = int( offset )
    img_ = np.roll( img_, (0,offset,0), axis=2)
    tkImage_ = ImageTk.PhotoImage( Image.fromarray(img_) )
    label_.config( image = tkImage_ )

def __init__(self):
    pass

def update_frame( ):
    global img_
    global speed_, slitWidth_
    global t_, label_, root_
    offset = int( speed_ * (time.time() - t_))
    t_ = time.time()
    generate_stripes( offset )
    print( 'updating frame' )
    root_.after( 100, update_frame )

def speed_changed( self, event ):
    global speed_ 
    speed_ = int(self.speed.get_value())
    print( 'New speed %d' % speed_ )
    return True

def width_changed( self, event ):
    global slitWidth_ 
    slitWidth_ = int(self.width.get_value())
    print( '[INFO] Width changed to %d' % slitWidth_ )
    init_arrays()
    return True

def init_tk():
    global tkImage_, root_
    global label_
    set_resolution()
    init_arrays()
    assert tkImage_
    label_ = tk.Label( root_, image = tkImage_ )
    label_.pack()

def main():
    global root_, t_
    t_ = time.time() 
    init_tk()
    root_.after( 100, update_frame )
    root_.mainloop()

if __name__ == '__main__':
    main()

