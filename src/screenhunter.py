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

import os
import gtk

import cream

from screenhunter.overlay import Overlay
from screenhunter.camera import Camera
from screenhunter.export import Exporter

class ScreenHunter(cream.Module): # Who shoots? Yeah, right.

    def __init__(self):
        
        cream.Module.__init__(self, 'org.sbillaudelle.ScreenHunter')
        
        self.camera = Camera()
        
        self.overlay = Overlay()
        
        self.overlay.connect('trigger', self.trigger_cb)
        self.overlay.connect('cancel', self.cancel_cb)
        self.overlay.show_all()


    def trigger_cb(self, source, selection):
        self.overlay.destroy()
        
        while gtk.events_pending():
            gtk.main_iteration()

        screenshot_path = self.camera.trigger()
        
        if selection:
            pb = gtk.gdk.pixbuf_new_from_file(screenshot_path).subpixbuf(*[int(i) for i in selection])
            pb.save(screenshot_path, 'png')

        Exporter(screenshot_path, os.path.join(self.context.get_path(), 'data/interface.ui'))
        self.quit()


    def cancel_cb(self, source):
        self.overlay.destroy()
        self.quit()


if __name__ == '__main__':
    ScreenHunter().main()
