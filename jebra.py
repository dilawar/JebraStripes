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
import time

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

from PIL import Image, ImageTk

realW_, w_, h_ = 800, 800, 480
img_           = None
tkImage_       = None
speed_         = 2**4            # pixel in seconds
slitWidth_     = 2**3             # in pixels.
t_             = time.time()
root_          = tk.Tk()
label_         = None
canvas_        = tk.Canvas( root_, width=w_, height=h_ )
imgOnCanvas_   = None
T_             = 10    # in ms
nrows_         = 10

def im2tkimg( img ):
    global realW_
    return ImageTk.PhotoImage(Image.fromarray(img))

def init_arrays():
    global img_
    global im_, tkImage_
    # numpy and opencv has incompatible coordinate system. So silly.
    print( 'I', end = '' )
    sys.stdout.flush()
    img_ = np.dstack([np.zeros((h_, w_), dtype = np.uint8) 
        for i in range(3)])
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
    #  print( 'Time = %.3f ' % t_ )
    offset = int( speed_ * (time.time() - t_))
    t_ = time.time()
    generate_stripes( offset )
    root_.after( T_, update_frame )

def speed_changed( newspeed ):
    global speed_ 
    newspeed = int(newspeed)
    speed_ = newspeed
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
    canvas_.grid(row=0, column=0, columnspan=2, rowspan = nrows_)
    init_arrays()
    assert tkImage_
    imgOnCanvas_ = canvas_.create_image( 0, 0
            , anchor = "nw"
            , image=tkImage_, state = tk.DISABLED
            )

    # add speed scale.
    speed = tk.Scale(root_, from_ = 10, to_ = 100
                , command= lambda v: speed_changed(v)
            )
    speed.config(orient = tk.HORIZONTAL)
    speed.grid(row=nrows_, column=0 )

    width = tk.Scale(root_, from_ = 5, to_ = 20
                , command= lambda v: width_changed(v)
            ) 
    width.set( slitWidth_ )
    width.config(orient = tk.HORIZONTAL)
    width.grid(row=nrows_, column = 1 )


def main():
    global root_, t_
    t_ = time.time() 
    init_tk()
    root_.after( 100, update_frame )
    root_.mainloop()

if __name__ == '__main__':
    main()

