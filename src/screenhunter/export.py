import sys
import os
import shutil
import gtk

from cream.util.subprocess import Subprocess
from cream.xdg.desktopentries import DesktopEntry

NAMING_PATTERN = 'Screenshot - {0:02}.png'
SCREENSHOT_DIR = '/tmp/screenshots/'

def get_applications():
    
    apps = []

    for entry in DesktopEntry.get_all():
        if isinstance(entry.mime_type, list) and 'image/png' in entry.mime_type:
            apps.append(entry)
            
    return apps


def get_filename():
    n = len(os.listdir(SCREENSHOT_DIR)) + 1
    return NAMING_PATTERN.format(n)


class Exporter:
    
    def __init__(self, screenshot_path, interface_path):
        
        self.screenshot_path = screenshot_path
        
        self.apps = get_applications()
        
        self.interface = gtk.Builder()
        self.interface.add_from_file(interface_path)
        
        self.export_dialog = self.interface.get_object('export_dialog')
        self.preview = self.interface.get_object('preview')
        self.liststore = self.interface.get_object('liststore')
        self.selector = self.interface.get_object('export_to_selector')
        self.filename = self.interface.get_object('filename')
        self.filechooser = self.interface.get_object('filechooser')
        self.export_radiobutton = self.interface.get_object('export_radiobutton')
        self.save_radiobutton = self.interface.get_object('save_radiobutton')

        self.filechooser.set_uri('file://' + SCREENSHOT_DIR + 'foo')
        self.filename.set_text(get_filename())
        
        for app in self.apps:
            theme = gtk.icon_theme_get_default()
            icon_info = theme.lookup_icon(app.icon, 16, 0)
            icon = gtk.gdk.pixbuf_new_from_file(icon_info.get_filename())
            icon = icon.scale_simple(16, 16, gtk.gdk.INTERP_HYPER)
            
            self.liststore.append((icon, app.name, app.exec_))
        
        pb = gtk.gdk.pixbuf_new_from_file(screenshot_path)
        w, h = pb.get_width(), pb.get_height()
        f = float(w) / float(h)
        pb = pb.scale_simple(int(160*f), 160, gtk.gdk.INTERP_HYPER)
        self.preview.set_from_pixbuf(pb)

        res = self.export_dialog.run()
        self.export_dialog.hide()
        
        if res:
            self.export()
        
        
    def export(self):
        
        if self.save_radiobutton.get_active():
            dest = os.path.join(self.filechooser.get_filename(), self.filename.get_text())
            shutil.move(self.screenshot_path, dest)
        elif self.export_radiobutton.get_active():
            active = self.selector.get_active()
            exec_ = self.liststore[active][2]
        
            exec_ = exec_.replace('%U', '')
            exec_ = exec_.replace('%u', '')
            exec_ = exec_.replace('%s', '')
            exec_ = exec_.replace('%F', '')

            Subprocess([exec_.strip(), self.screenshot_path]).run()
