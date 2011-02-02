#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import tempfile
import gtk
import gst

class Camera:

    def __init__(self):
        
        self.pipeline = gst.parse_launch('ximagesrc ! ffmpegcolorspace ! videoscale ! video/x-raw-rgb,framerate=1/1,red_mask=(int)0xff0000,green_mask=(int)0x00ff00,blue_mask=(int)0x0000ff ! appsink name=sink')
        
        self.sink = self.pipeline.get_by_name('sink')


    def trigger(self):

        self.pipeline.set_state(gst.STATE_PLAYING)

        path = tempfile.mktemp('.png')
        buf = self.sink.emit('pull-buffer')

        caps = dict([(k.strip(), v.strip()) for k, v in [c.split('=') for c in buf.caps.to_string().split(',')[1:]]])

        width = int(caps['width'].split(')')[1])
        height = int(caps['height'].split(')')[1])

        pb = gtk.gdk.pixbuf_new_from_data(buf, gtk.gdk.COLORSPACE_RGB, False, 8, width, height, width*3)
        pb.save(path, 'png')

        self.pipeline.set_state(gst.STATE_PAUSED)

        return path
