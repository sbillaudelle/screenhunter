import math
import gobject
import gtk
import cairo

ICON_SIZE = 32

def rounded_rectangle(cr, x, y, w, h, r=20):

    if r >= h / 2.0:
        r = h / 2.0

    cr.arc(x + r, y + r, r, math.pi, -.5 * math.pi)
    cr.arc(x + w - r, y + r, r, -.5 * math.pi, 0 * math.pi)
    cr.arc(x + w - r, y + h - r, r, 0 * math.pi, .5 * math.pi)
    cr.arc(x + r, y + h - r, r, .5 * math.pi, math.pi)
    cr.close_path()


class Overlay(gtk.Window):
    
    __gsignals__ = {
        'trigger': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'cancel': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self):

        gtk.Window.__init__(self)
    
        self._selection = None
        self._selecting = False

        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.stick()
        self.set_keep_above(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_app_paintable(True)
        self.set_colormap(self.get_screen().get_rgba_colormap())
        self.fullscreen()
        
        self.set_events(self.get_events() | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
        
        self.connect('expose-event', self.expose_cb)
        self.connect('button-press-event', self.button_press_cb)
        self.connect('button-release-event', self.button_release_cb)
        self.connect('motion-notify-event', self.motion_cb)

        self.display = self.get_display()
        self.screen = self.display.get_default_screen()
        width, height = self.screen.get_width(), self.screen.get_height()

        self.set_size_request(width, height)

        self.move(0, 0)
        
        
    def reset_selection(self):
        self._selection = None
        
    def get_selection(self):
        return self._selection
        
        
    def expose_cb(self, window, event):
        
        width, height = self.get_size()

        ctx = self.window.cairo_create()
        ctx.set_line_width(1)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()

        selection = self.get_selection()
        if selection:# and (selection[2] != 0 and selection[3] != 0):
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.set_source_rgba(0, 0, 0, 0.5)
            ctx.paint()

            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.rectangle(selection[0], selection[1], selection[2], selection[3])
            ctx.fill()

            ctx.set_source_rgba(1, 1, 1, .4)
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.rectangle(selection[0] + .5, selection[1] + .5, selection[2], selection[3])
            ctx.stroke()

        theme = gtk.icon_theme_get_default()
        icon_record_info = theme.lookup_icon('gtk-media-record', 32, 0)
        icon_cancel_info = theme.lookup_icon('gtk-cancel', 32, 0)
        icon_record = gtk.gdk.pixbuf_new_from_file(icon_record_info.get_filename())
        icon_cancel = gtk.gdk.pixbuf_new_from_file(icon_cancel_info.get_filename())
        
        icon_record_width = icon_record.get_width()
        icon_record_height = icon_record.get_height()

        icon_cancel_width = icon_cancel.get_width()
        icon_cancel_height = icon_cancel.get_height()
        
        x = (width - icon_record_width - icon_cancel_width - 5) / 2
        y = int(height * .8)
        ctx.translate(x, y)

        ctx.save()
        rounded_rectangle(ctx, -5, -5, icon_record_width + icon_cancel_width + 10, max(icon_record_height, icon_cancel_height) + 10)
        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.6)
        ctx.stroke()
        ctx.restore()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_pixbuf(icon_record, 0, 0)
        ctx.paint()

        ctx.translate(icon_record_width + 0, 0)
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_pixbuf(icon_cancel, 0, 0)
        ctx.paint()


    def draw(self):

        if self.window:
            self.window.invalidate_rect(self.allocation, True)
            
            
    def button_press_cb(self, window, event):
            
        width, height = self.get_size()

        theme = gtk.icon_theme_get_default()
        icon_record_info = theme.lookup_icon('gtk-media-record', 32, 0)
        icon_cancel_info = theme.lookup_icon('gtk-cancel', 32, 0)
        icon_record = gtk.gdk.pixbuf_new_from_file(icon_record_info.get_filename())
        icon_cancel = gtk.gdk.pixbuf_new_from_file(icon_cancel_info.get_filename())
        
        record_width = icon_record.get_width()
        record_height = icon_record.get_height()

        cancel_width = icon_cancel.get_width()
        cancel_height = icon_cancel.get_height()

        record_x = (width - record_width - cancel_width) / 2
        record_y = int(height * .8)
        cancel_x = (width - record_width - cancel_width) / 2 + record_width
        cancel_y = int(height * .8)

        if event.x >= record_x and event.x <= record_x + record_width and event.y >= record_y and event.y <= record_y + record_height:
            pass
        elif event.x >= cancel_x and event.x <= cancel_x + cancel_width and event.y >= cancel_y and event.y <= cancel_y + cancel_height:
            pass
        else:
            self._selecting = True

            self._selection = (event.x, event.y, 0, 0)
            self.draw()


    def button_release_cb(self, window, event):
            
        width, height = self.get_size()

        theme = gtk.icon_theme_get_default()
        icon_record_info = theme.lookup_icon('gtk-media-record', 32, 0)
        icon_cancel_info = theme.lookup_icon('gtk-cancel', 32, 0)
        icon_record = gtk.gdk.pixbuf_new_from_file(icon_record_info.get_filename())
        icon_cancel = gtk.gdk.pixbuf_new_from_file(icon_cancel_info.get_filename())
        
        record_width = icon_record.get_width()
        record_height = icon_record.get_height()

        cancel_width = icon_cancel.get_width()
        cancel_height = icon_cancel.get_height()

        record_x = (width - record_width - cancel_width) / 2
        record_y = int(height * .8)
        cancel_x = (width - record_width - cancel_width) / 2 + record_width
        cancel_y = int(height * .8)

        if (not self._selecting) and event.x >= record_x and event.x <= record_x + record_width and event.y >= record_y and event.y <= record_y + record_height:
            self.emit('trigger', self.get_selection())
        elif (not self._selecting) and event.x >= cancel_x and event.x <= cancel_x + cancel_width and event.y >= cancel_y and event.y <= cancel_y + cancel_height:
            self.emit('cancel')
        elif self._selecting:
            sel = self._selection

            if event.x == sel[0] and event.y == sel[1]:
                self._selection = None
                self.draw()
                self._selecting = False
                return

            self._selection = (sel[0], sel[1], event.x - sel[0], event.y - sel[1])
            self.draw()
        
            self._selecting = False


    def motion_cb(self, window, event):
        
        if self._selecting and self._selection:
            sel = self._selection
        
            self._selection = (sel[0], sel[1], event.x - sel[0], event.y - sel[1])
            self.draw()

