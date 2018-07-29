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
import cv2

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

from PIL import Image, ImageTk

realW_, w_, h_ = 0, 0, 0
img_           = None
tkImage_       = None
speed_         = 100            # pixel in seconds
slitWidth_     = 20             # in pixels.
t_             = time.time()
root_          = tk.Tk()
label_         = None
canvas_        = tk.Canvas( root_ )
imgOnCanvas_   = None
T_             = 20    # in ms

def set_resolution():
    global w_, h_
    global img_
    global canvas_, root_
    monitor = screeninfo.get_monitors()[-1]
    w_ = monitor.width // 2
    realW_ = w_
    h_ = monitor.height  // 2
    # make sure that width is divisible by slitWidth_ and must be even and
    # slightly larger than the screen width so we don't see uneven gaps.
    nSlits = w_ // slitWidth_
    nSlits = nSlits - (nSlits % 2 ) + 1
    w_ = nSlits * slitWidth_
    root_.geometry( '{}x{}'.format( realW_, h_) )
    canvas_.width = realW_
    canvas_.height = h_
    canvas_.grid( row = 0, column = 0, columnspan = 2 )
    print( 'New dim for image %d, monitory width %d' % (w_, realW_))

def im2tkimg( img ):
    global realW_
    return ImageTk.PhotoImage(Image.fromarray( img[:,0:realW_-1,:]))

def init_arrays():
    global img_
    global im_, tkImage_
    # numpy and opencv has incompatible coordinate system. So silly.
    print( 'I', end = '' )
    sys.stdout.flush()
    img_ = np.dstack([np.zeros( (h_, w_), dtype = np.uint8) for i in range(3)])
    #  print( img_.shape )
    for i in range( 0, w_, 2*slitWidth_ ):
        img_[:,i:i+slitWidth_,:] = 255
    tkImage_ = im2tkimg(img_)

def generate_stripes( offset = 0 ):
    global speed_, slitWidth_ 
    global tkImage_, canvas_
    global img_
    offset = int( offset )
    img_ = np.roll( img_, (0,offset,0), axis=1)
    tkImage_ = im2tkimg( img_ )
    canvas_.itemconfig( imgOnCanvas_, image = tkImage_ )

def update_frame( ):
    global img_
    global speed_, slitWidth_
    global t_, label_, root_
    global canvas_, imgOnCanvas_
    print( 'Time = %.3f ' % t_ )
    offset = int( speed_ * (time.time() - t_))
    t_ = time.time()
    generate_stripes( offset )
    root_.after( T_, update_frame )

def speed_changed( newspeed ):
    global speed_ 
    speed_ = int(newspeed)
    print( 'New speed %d' % newspeed )
    return True

def width_changed( width ):
    global slitWidth_ 
    slitWidth_ = int(width)
    print( '[INFO] Width changed to %d' % slitWidth_ )
    init_arrays()
    return True

def init_tk():
    global tkImage_, root_
    global canvas_, imgOnCanvas_
    global label_
    set_resolution()
    init_arrays()
    assert tkImage_
    imgOnCanvas_ = canvas_.create_image(h_//2, realW_//2, image=tkImage_
            , state = tk.DISABLED
            )

    # add speed scale.
    speed = tk.Scale(root_, from_ = 50, to_ = 500
                , command= lambda v: speed_changed(v)
            )
    speed.config(orient = tk.HORIZONTAL)
    speed.grid(row = 1, column = 0)

    width = tk.Scale(root_, from_ = 50, to_ = 500
                , command= lambda v: width_changed(v)
            ) 
    width.config(orient = tk.HORIZONTAL)
    width.grid(row = 1, column = 1)
    

def main():
    global root_, t_
    t_ = time.time() 
    init_tk()
    root_.after( 100, update_frame )
    root_.mainloop()

if __name__ == '__main__':
    main()

