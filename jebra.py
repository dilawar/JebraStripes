#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""jebra.py: 

NOTE: The raw image which we operate on is 4x time larger in width to make sure
we get right number of pixel to offset. The figure which is displayed is
downsampled 4x. Otherwise the picture flow will not be smooth.

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
try:
    import Tkinter as tk
except ImportError as e:
    import tkinter as tk

from PIL import Image, ImageTk
import RPi.GPIO as GPIO
input_pin_ = 21


def init_pins():
    global input_pin_
    GPIO.setmode( GPIO.BCM )
    GPIO.setup(input_pin_, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


datadir_ = os.path.join( os.getenv( 'HOME' ), 'Desktop', 'Experiments' )
if not os.path.isdir( datadir_ ):
    os.makedirs( datadir_ )

stamp = datetime.datetime.now().isoformat().replace( ' ', '')
datafile_ = os.path.join( datadir_, stamp )
with open( datafile_, 'w' ) as f:
    f.write( 'timestamp running \n')

step_        = 0
status_      = 'RUNNING'
w_, h_, ws_  = 800, 480, 1
img_         = None
tkImage_     = None
speed_       = 10               # mm in seconds
slitWidth_   = 5                # in mm.
t_           = time.time()
root_        = tk.Tk()
root_.attributes( '-zoomed', True )
label_       = None
canvas_      = tk.Canvas( root_, width=w_, height=h_ )
startStop_   = None             # start stop button
imgOnCanvas_ = None
T_           = 30    # in ms
nrows_       = 10
density_     = ((w_**2 + h_**2)**0.5)/5/25.4   # per mm

print( '[INFO] Density %.2f per mm' % density_ )
print( '[WARN] This is customized for 5" LCD display. The values you'
       ' see on the development machine might vary if screen resolution '
       ' is not 800x480. '
       ' You have been warned!' )

def im2tkimg( img ):
    global realW_
    h, w  = img.shape 
    img = scipy.misc.imresize(img, (h, int(w*ws_)))
    return ImageTk.PhotoImage(Image.fromarray(img))

def mm2px( mm ):
    return int(mm * density_)

def px2mm( px ):
    return px / density_

def append_data_line( filename ):
    stamp = datetime.datetime.now().isoformat()
    line = '%s %g\n' % (stamp, status_ )
    with open( filename, 'a' ) as f:
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
    tkImage_ = im2tkimg(img_ )


def generate_stripes( offset ):
    global speed_, slitWidth_ 
    global tkImage_, canvas_
    global img_
    if status_ == 'STOPPED':
        return 
    offset = int( offset )
    #img_ = np.roll( img_, (0,offset), axis=1)
    img_ = np.roll( img_, offset, axis=1)
    tkImage_ = im2tkimg( img_ )
    canvas_.itemconfig( imgOnCanvas_, image = tkImage_ )

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
    step_ += 1
    dt = time.time() - t_
    t_ = time.time()
    offset = speed_ * density_ * dt
    s = offset / density_ / ws_ / dt 
    if step_ % 25 == 0:
        print( 'OFFSET %d, dt=%.2f ms speed=%.2f mm/s' % ( offset, dt*1000, s ) )
    generate_stripes( intOffset(offset) )
    s = GPIO.input( input_pin_ )
    if s == 1:
        status_ = 'STOPPED'
    else:
        status_ = 'RUNNING'
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

def init_tk():
    global tkImage_, root_
    global canvas_, imgOnCanvas_
    global startStop_

    canvas_.grid(row=0, column=0, columnspan=3, rowspan = nrows_)
    init_arrays()
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
    t_ = time.time() 
    init_pins()
    init_tk()
    root_.after( T_, update_frame )
    root_.mainloop()

if __name__ == '__main__':
    main()

