#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""jebra.py: 

NOTE: The raw image which we operate on is 4x time larger in width to make sure
we get right number of pixel to offset. The figure which is displayed is
downsampled 4x. Otherwise the picture flow will not be smooth.

[WARN] This is customized for 5" LCD display. The values you see on the development
machine might vary if screen resolution is not 800x480. You have been warned!

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
import random
import scipy.misc
import datetime
import cv2
from PIL import Image, ImageTk

try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk


onPi_   = True
use_tk_ = False

# opencv window
window_ = 'FISH'
cv2.namedWindow( window_, cv2.WINDOW_AUTOSIZE )


try:
    import RPi.GPIO as GPIO
except Exception as e:
    print( '[WARN] Not running on rPI' )
    onPi_ = False

input_pin_   = 21
step_        = 0
status_      = 'RUNNING'
w_, h_, ws_  = 800, 480, 1
img_         = None
tkImage_     = None
speed_       = 10               # mm in seconds
slitWidth_   = 5                # in mm.
t_           = time.time()
startStop_   = None             # start stop button
imgOnCanvas_ = None
T_           = 30    # in ms
nrows_       = 10
density_     = ((w_**2 + h_**2)**0.5)/5/25.4   # per mm

if use_tk_:
    root_        = tk.Tk()
    label_       = None
    canvas_      = tk.Canvas( root_, width=w_, height=h_ )

datadir_ = os.path.join( os.getenv( 'HOME' ), 'Desktop', 'Experiments' )
if not os.path.isdir( datadir_ ):
    os.makedirs( datadir_ )

stamp = datetime.datetime.now().isoformat().replace( ' ', '')
datafile_ = os.path.join( datadir_, stamp )
with open( datafile_, 'w' ) as f:
    f.write( 'timestamp running \n')

def init_pins():
    global input_pin_
    global onPi_ 
    if not onPi_:
        return
    GPIO.setmode( GPIO.BCM )
    GPIO.setup(input_pin_, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def toggle_fullscreen(event=None):
    global root_
    root_.attributes("-fullscreen", True )
    return "break"

def end_fullscreen( event=None):
    global root_
    root_.attributes("-fullscreen", False)
    return "break"

def im2tkimg( img ):
    global realW_
    h, w  = img.shape 
    img = scipy.misc.imresize(img, (h, int(w*ws_)))
    return ImageTk.PhotoImage(Image.fromarray(img))

def mm2px( mm ):
    return int(mm * density_)

def px2mm( px ):
    return px / density_

def append_data_line( ):
    global datafile_
    stamp = datetime.datetime.now().isoformat()
    line = '%s %s\n' % (stamp, status_ )
    with open( datafile_, 'a' ) as f:
        f.write( line )

def init_arrays():
    global img_
    global im_, tkImage_
    # numpy and opencv has incompatible coordinate system. So silly.
    print( 'I', end = '' )
    sys.stdout.flush()
    img_ = np.zeros( (h_, w_ * ws_), dtype=np.uint8 )
    stride = ws_ * mm2px( slitWidth_ )
    for i in range( 0, w_ * ws_, 2*stride ):
        img_[:,i:i+stride] = 255

    if use_tk_:
        tkImage_ = im2tkimg(img_ )

def generate_stripes( offset ):
    global speed_, slitWidth_ 
    global tkImage_, canvas_
    global img_
    if status_ == 'STOPPED':
        return 
    offset = int( offset )
    assert img_ is not None
    img_ = np.roll( img_, offset, axis=1)
    if use_tk_:
        tkImage_ = im2tkimg( img_ )
        canvas_.itemconfig( imgOnCanvas_, image = tkImage_ )
    else:
        cv2.imshow( window_, img_ )
        cv2.waitKey( 1 )

def intOffset( v ):
    px = int(v)
    frac = v - px
    if random.random() < frac:
        px += 1
    return px

def update_frame( ):
    global img_
    global speed_, slitWidth_, density_
    global t_, label_, root_
    global canvas_, imgOnCanvas_
    global step_, status_

    append_data_line()
    step_ += 1
    dt = time.time() - t_
    t_ = time.time()
    offset = speed_ * density_ * dt
    s = offset / density_ / ws_ / dt 
    if step_ % 25 == 0:
        print( 'OFFSET %d, dt=%.2f ms speed=%.2f mm/s' % ( offset, dt*1000, s ) )
    generate_stripes( intOffset(offset) )

    if onPi_:
        s = GPIO.input( input_pin_ )
        if s == 1:
            status_ = 'STOPPED'
        else:
            status_ = 'RUNNING'

    if use_tk_:
        root_.after( T_, update_frame )


def speed_changed( newspeed ):
    global speed_ 
    newspeed = ws_ * int(newspeed)
    speed_ = newspeed
    print( 'New speed %d' % newspeed )
    return True

def width_changed( width ):
    global slitWidth_ 
    slitWidth_ = float( width )
    print( '[INFO] Width changed to %d mm' % slitWidth_ )
    init_arrays()
    return True

def toggle_start_stop( ):
    global status_
    global startStop_
    if status_ == 'RUNNING':
        status_ = 'STOPPED'
    else:
        status_ = 'RUNNING'

    startStop_.config( text = status_ )

def init_tk( show_control ):
    global tkImage_, root_
    global canvas_, imgOnCanvas_
    global startStop_

    root_.bind("<F11>", toggle_fullscreen)
    root_.bind("<Escape>", end_fullscreen)

    canvas_.grid(row=0, column=0, columnspan=3, rowspan = nrows_)
    assert tkImage_
    imgOnCanvas_ = canvas_.create_image( 0, 0
            , anchor = "nw"
            , image=tkImage_, state = tk.DISABLED
            )

    # add speed scale.
    speed = tk.Scale(root_, from_ = 5, to_ = 20
                , label = 'mm/s'
                , command= lambda v: speed_changed(v)
            )
    speed.config(orient = tk.HORIZONTAL)
    speed.grid(row=nrows_, column=0 )
    speed.set( speed_ )

    width = tk.Scale(root_, from_ = 2, to_ = 10
                , label = 'mm'
                , command= lambda v: width_changed(v)
            ) 
    width.set( slitWidth_ )
    width.config(orient = tk.HORIZONTAL)
    width.grid(row=nrows_, column = 1 )

    # toggle step/stop
    startStop_ = tk.Button( text= status_  
            , command = toggle_start_stop
            )
    startStop_.grid( row=nrows_, column=2 )

def main():
    global root_, t_
    print( '[INFO] Density %.2f per mm' % density_ )
    t_ = time.time( ) 
    init_pins( )
    init_arrays()

    if use_tk_:
        init_tk( )
        root_.after( T_, update_frame )
        root_.mainloop( )
    else:
        while True:
            update_frame( )

if __name__ == '__main__':
    main()

