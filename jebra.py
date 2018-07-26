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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, GObject

w_, h_     = 0, 0
img_       = None
speed_     = 100            # pixel in seconds
slitWidth_ = 100        # in pixels.
t_         = time.time()

def set_resolution():
    global w_, h_
    global img_
    monitor = screeninfo.get_monitors()[-1]
    w_ = monitor.width  // 2

    # make sure that width is divisible by slitWidth_ and must be even.
    nSlits = w_ // slitWidth_ 
    nSlits = nSlits - (nSlits % 2 )
    w_ = nSlits * slitWidth_
    h_ = monitor.height // 2

def init_arrays():
    global img_
    # numpy and opencv has incompatible coordinate system. So silly.
    img_ = np.zeros( (3, h_, w_), dtype = np.uint8 )
    for i in range( 0, w_, 2*slitWidth_ ):
        img_[:,:,i:i+slitWidth_] = 255

def show_frame(  waitFor = 1 ):
    global img_
    global windowName_
    cv2.imshow( windowName_, img_ )
    cv2.waitKey( waitFor )

def generate_stripes( offset = 0 ):
    global speed_, slitWidth_ 
    global img_
    offset = int( offset )
    img_ = np.roll( img_, (0,0,offset), axis=2)

def np2pixbuf( im ):
    """Convert Pillow image to GdkPixbuf"""
    data = im.tobytes()
    d, h, w = im.shape
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
            False, 8, w, h, w * 3)
    return pix

class JebraWindow( Gtk.ApplicationWindow ):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Jebra", application=app)
        self.set_default_size(300, 300)

        vbox = Gtk.VBox()
        self.add( vbox )

        # create an image
        image = Gtk.Image()
        # set the content of the image as the file filename.png
        image.set_from_pixbuf( np2pixbuf(img_) )
        # add the image to the window
        vbox.pack_start(image, True, True, 0)

        ## Add scale.
        self.speed = Gtk.Scale( )
        self.speed.set_range(100, 1000)
        vbox.pack_start( self.speed, True, True, 0 )
        self.speed.connect( "value-changed", self.speed_changed )
        self.speed.show()

        image.show()
        self.show_all()

        # Add timer. Call as fast as you can otherwise it would be visible to
        # fish.
        GObject.timeout_add( 10, self.update_frame, image )

    def update_frame( self, image ):
        global img_
        global speed_, slitWidth_
        global t_
        offset = int( speed_ * (time.time() - t_))
        t_ = time.time()
        print( 'Offset is %d' % offset )
        generate_stripes( offset )
        image.set_from_pixbuf( np2pixbuf(img_) )
        return True

    def speed_changed( self, event ):
        global speed_ 
        speed_ = int(self.speed.get_value())
        print( 'New speed %d' % speed_ )
        return True


class JebraApp( Gtk.Application ):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = JebraWindow(self)
        win.connect( "destroy", Gtk.main_quit )
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

def main():
    set_resolution()
    init_arrays()
    t0 = time.time() 
    app = JebraApp()
    GLib.unix_signal_add( GLib.PRIORITY_DEFAULT, signal.SIGINT, app.quit )
    e = app.run( )
    sys.exit( e )

if __name__ == '__main__':
    main()

