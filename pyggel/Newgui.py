"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import image, view, font, event
import time

class Packer(object):
    def __init__(self, app=None, packtype="wrap", size=(10,10)):
        self.app = app
        self.packtype = packtype
        self.size = size

        self.need_to_pack = False

    def pack(self):
        self.app.widgets.reverse()
        getattr(self, "pack_%s"%self.packtype)()
        self.app.widgets.reverse()
        self.need_to_pack = False

    def pack_wrap(self):
        nw = 0
        nh = 0
        newh = 0

        for i in self.app.widgets:
            if isinstance(i, NewLine):
                nw = 0
                nh += newh + i.size[1]
                newh = 0
                i.pos = (nw, nh)
                continue
            if i.override_pos:
                continue
            w, h = i.size
            if nw + w > self.size[0] and nw:
                nh += newh + 1
                newh = h
                nw = w
                pos = (0, nh)
            else:
                pos = (nw, nh)
                nw += w
                if h > newh:
                    newh = h
            i.force_pos_update(pos)

    def pack_center(self):
        rows = [[]]
        w = 0
        for i in self.app.widgets:
            if isinstance(i, NewLine):
                rows.append([i])
                rows.append([])
                continue
            if i.override_pos:
                continue
            rows[-1].append(i)
            w += i.size[0]
            if w >= self.size[0]:
                rows.append([])
                w = 0

        sizes = []
        for row in rows:
            h = 0
            w = 0
            for widg in row:
                if widg.size[1] > h:
                    h = widg.size[1]
                w += widg.size[0]
            sizes.append((w, h))

        center = self.size[1] / 2
        height = 0
        for i in sizes:
            height += i[1]
        top = center - height / 2
        for i in xrange(len(rows)):
            w = self.size[0] / 2 - sizes[i][0] / 2
            for widg in rows[i]:
                widg.force_pos_update((w, top))
                w += widg.size[0]
            top += sizes[i][1]

    def pack_None(self):
        nw = 0
        nh = 0
        newh = 0

        for i in self.app.widgets:
            if isinstance(i, NewLine):
                nw = 0
                nh += newh + i.size[1]
                newh = 0
                i.pos = (nw, nh)
                continue
            if i.override_pos:
                continue
            w, h = i.size
            pos = (nw, nh)
            nw += w
            if h > newh:
                newh = h
            i.force_pos_update(pos)

class App(object):
    """A simple Application class, to hold and control all widgets."""
    def __init__(self, event_handler):
        """Create the App.
           event_handler must be the event.Handler object that the gui will use to get events,
           and each event handler may only have on App attached to it."""
        self.event_handler = event_handler
        self.event_handler.gui = self

        self.widgets = []

        self.dispatch = event.Dispatcher()

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.packer = Packer(self, size=view.screen.screen_size)

        self.visible = True

    def get_mouse_pos(self):
        """Return mouse pos based on App position - always (0,0)"""
        return view.screen.get_mouse_pos()

    def new_widget(self, widget):
        """Add a new widget to the App."""
        if not widget in self.widgets:
            self.widgets.insert(0, widget)
            if not widget.override_pos:
                self.packer.need_to_pack = True

    def handle_mousedown(self, button, name):
        """Callback for mouse click events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousedown(button, name):
                    return True
        return False

    def handle_mouseup(self, button, name):
        """Callback for mouse release events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mouseup(button, name):
                    return True
        return False

    def handle_mousehold(self, button, name):
        """Callback for mouse hold events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousehold(button, name):
                    return True
        return False

    def handle_mousemotion(self, change):
        """Callback for mouse motion events from event_handler."""
        for i in self.widgets:
            if i.handle_mousemotion(change):
                return True

    def handle_uncaught_event(self, event):
        """Callback for uncaught_event events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_uncaught_event(event):
                    return True
        return False

    def handle_keydown(self, key, string):
        """Callback for key press events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keydown(key, string):
                    return True
        return False

    def handle_keyup(self, key, string):
        """Callback for key release events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyup(key, string):
                    return True
        return False

    def handle_keyhold(self, key, string):
        """Callback for key hold events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyhold(key, string):
                    return True
        return False

    def next_widget(self):
        """Cycle widgets so next widget is top one."""
        self.widgets.append(self.widgets.pop(0))
        while not self.widgets[0].visible:
            self.widgets.append(self.widgets.pop(0))

    def set_top_widget(self, widg):
        """Moves widget 'widg' to top position."""
        if widg in self.widgets:
            self.widgets.remove(widg)
        self.widgets.insert(0, widg)
        for i in self.widgets:
            if not i == widg:
                i.unfocus()

    def render(self, camera=None):
        """Renders all widgets, camera can be None or the camera object used to render the scene."""
        self.widgets.reverse()
        for i in self.widgets:
            if i.visible: i.render()
        self.widgets.reverse()

class Widget(object):
    def __init__(self, app, pos=None):
        self.app = app
        self.pos = pos
        self.size = (0,0)
        if pos:
            self.override_pos = True
        else:
            self.override_pos = False

        self.dispatch = event.Dispatcher()

        self.visible = True
        self.app.new_widget(self)
        self.image = None

        self._mhold = False
        self._mhover = False
        self.key_active = False
        self.key_hold_lengths = {}
        self.khl = 150 #milliseconds to hold keys for repeat!

    def pack(self):
        self.app.packer.pack()

    def _collidem(self):
        x, y = self.app.get_mouse_pos()
        a, b = self.pos
        w, h = self.size
        return (x >= a and x <= a+w) and (y >= b and y <= b+h)

    def focus(self):
        self.app.set_top_widget(self)
        self.key_active = True

    def handle_mousedown(self, button, name):
        if name == "left":
            if self._mhover:
                self._mhold = True
                self.focus()
                return True
            self.unfocus()

    def handle_mouseup(self, button, name):
        if name == "left":
            if self._mhold and self._mhover:
                self._mhold = False
                self.dispatch.fire("click")
                return True

    def handle_mousehold(self, button, name):
        if name == "left":
            if self._mhold:
                return True

    def handle_mousemotion(self, change):
        self._mhover = self._collidem()
        for i in self.app.widgets:
            if not i == self:
                i._mhover = False
        return self._mhover

    def can_handle_key(self, key, string):
        return False

    def handle_keydown(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                self.dispatch.fire("keypress", key, string)
                return True

    def handle_keyhold(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key in self.key_hold_lengths:
                    if time.time() - self.key_hold_lengths[key] >= self.khl*0.001:
                        self.handle_keydown(key, string)
                        self.key_hold_lengths[key] = time.time()
                else:
                    self.key_hold_lengths[key] = time.time()
                return True

    def handle_keyup(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key in self.key_hold_lengths:
                    del self.key_hold_lengths[key]
                return True

    def handle_uncaught_event(self, event):
        pass

    def force_pos_update(self, pos):
        self.pos = pos

    def render(self, offset=(0,0)):
        if self.image:
            x, y = self.pos
            x += offset[0]
            y += offset[1]
            self.image.pos = (x, y)
            self.image.render()
            self.image.pos = self.pos #need to reset!

    def unfocus(self):
        self.key_active=False
        self.key_hold_lengths = {}

class Frame(App, Widget):
    def __init__(self, app, pos=None, size=(10,10)):
        Widget.__init__(self, app, pos)
        self.size = size

        self.widgets = []

        self.mefont = self.app.mefont
        self.regfont = self.app.regfont

        self.packer = Packer(self, size=self.size)
        self.pack()

    def get_mouse_pos(self):
        x, y = self.app.get_mouse_pos()
        x -= self.pos[0]
        y -= self.pos[1]
        return x, y

    def handle_mousedown(self, button, name):
        Widget.handle_mousedown(self, button, name)
        if self._mhover:
            return App.handle_mousedown(self, button, name)

    def handle_mouseup(self, button, name):
        if self._mhold:
            Widget.handle_mouseup(self, button, name)
            return App.handle_mouseup(self, button, name)

    def handle_mousehold(self, button, name):
        Widget.handle_mousehold(self, button, name)
        if self._mhold:
            return App.handle_mousehold(self, button, name)

    def handle_mousemotion(self, change):
        Widget.handle_mousemotion(self, change)
        if self._mhover:
            return App.handle_mousemotion(self, change)
        for i in self.widgets:
            i._mhover = False

    def render(self, offset=(0,0)):
        view.screen.push_clip2d(self.pos, self.size)
        self.widgets.reverse()

        x, y = self.pos
        x += offset[0]
        y += offset[1]
        offset = (x, y)
        for i in self.widgets:
            if i.visible: i.render(offset)
        self.widgets.reverse()
        view.screen.pop_clip()

class NewLine(Widget):
    def __init__(self, app, height=0):
        Widget.__init__(self, app)
        self.size = (0, height)
        self.pack()

class Label(Widget):
    def __init__(self, app, start_text="", pos=None):
        Widget.__init__(self, app, pos)

        self.text = start_text
        self.image = self.app.mefont.make_text_image(self.text)
        self.size = self.image.get_size()
        self.pack()

class Button(Widget):
    def __init__(self, app, text, pos=None, callbacks=[]):
        Widget.__init__(self, app, pos)
        self.text = text
        self.ireg = self.app.mefont.make_text_image(self.text)
        self.ihov = self.app.mefont.make_text_image(self.text, (1, 0, 0, 1))
        self.icli = self.app.mefont.make_text_image(self.text, (0, 1, 0, 1))
        self.image = self.ireg
        self.size = self.image.get_size()

        for i in callbacks:
            self.dispatch.bind("click", i)

        self.pack()

        self.handle_mousemotion((0,0)) #make sure we are set to hover at start if necessary!

    def render(self, offset=(0,0)):
        if self._mhover:
            if self._mhold:
                self.image = self.icli
            else:
                self.image = self.ihov
        else:
            self.image = self.ireg
        Widget.render(self, offset)

class Checkbox(Widget):
    def __init__(self, app, pos=None):
        Widget.__init__(self, app, pos)

        self.off = self.app.regfont.make_text_image("( )")
        self.on = self.app.regfont.make_text_image("(!)")
        self.image = self.off

        self.state = 0

        self.size = self.off.get_size()

        self.dispatch.bind("click", self._change_state)

    def _change_state(self):
        self.state = abs(self.state-1)

    def render(self, offset):
        if self.state:
            self.image = self.on
        else:
            self.image = self.off
        Widget.render(self, offset)

class Radio(Frame):
    def __init__(self, app, pos=None, options=[]):
        Frame.__init__(self, app, pos)
        self.packer.packtype = None

        self.options = []
        self.states = {}

        w = 0
        for i in options:
            c = Checkbox(self)
            if not self.options:
                c.state = 1
            c.dispatch.bind("click", self.check_click)
            l = Label(self, i)
            NewLine(self)
            self.options.append([i, c, l, c.state])
            self.states[i] = c.state

            _w = l.pos[0]+l.size[0]
            if _w > w:
                w = _w
        h = max((c.pos[1]+c.size[1],
                 l.pos[1]+l.size[1]))

        self.size = (w, h)
        self.pack()

    def check_click(self):
        for i in self.options:
            name, check, label, state = i
            if check.state != state: #changed!
                if check.state: #selected!
                    for x in self.options:
                        if not i == x:
                            x[1].state = 0
                            x[3] = 0
                            self.states[x[0]] = 0
                    state = 1
                else:
                    check.state = 1
            i[0], i[1], i[2], i[3] = name, check, label, state
            self.states[name] = state

class MultiChoiceRadio(Radio):
    def __init__(self, app, pos=None, options=[]):
        Radio.__init__(self, app, pos, options)

    def check_click(self):
        for i in self.options:
            name, check, label, state = i
            state = check.state
            i[0], i[1], i[2], i[3] = name, check, label, state
            self.states[name] = state

class Input(Widget):
    def __init__(self, app, start_text="", width=100, pos=None):
        Widget.__init__(self, app, pos)

        self.text = start_text
        self.image = self.app.mefont.make_text_image(self.text)

        self.size = (width, self.app.mefont.pygame_font.get_height())

        self.cursor_pos = len(self.text)
        self.cursor_image = image.Animation(((self.app.regfont.make_text_image("|"), .5),
                                             (self.app.regfont.make_text_image("|",color=(0,0,0,0)), .5)))
        self.cwidth = int(self.cursor_image.get_width()/2)
        self.xwidth = self.size[0] - self.cwidth*2
        self.pack()

    def can_handle_key(self, key, string):
        if string and string in self.app.mefont.acceptable:
            return True
        if key in (K_LEFT, K_RIGHT, K_END, K_HOME, K_DELETE,
                   K_BACKSPACE, K_RETURN):
            return True
        return False

    def submit_text(self):
        if self.text:
            self.dispatch.fire("submit", self.text)
        self.text = ""
        self.image.text = ""
        self.working = 0

    def move_cursor(self, x):
        """Move the cursor position."""
        self.cursor_image.reset()
        self.cursor_pos += x
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        if self.cursor_pos > len(self.text):
            self.cursor_pos = len(self.text)

    def handle_keydown(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key == K_LEFT:
                    self.move_cursor(-1)
                elif key == K_RIGHT:
                    self.move_cursor(1)
                elif key == K_HOME:
                    self.cursor = 0
                elif key == K_END:
                    self.cursor = len(self.text)
                elif key == K_DELETE:
                    self.text = self.text[0:self.cursor_pos]+self.text[self.cursor_pos+1::]
                    self.image.text = self.text
                elif key == K_BACKSPACE:
                    if self.cursor_pos:
                        self.text = self.text[0:self.cursor_pos-1]+self.text[self.cursor_pos::]
                        self.move_cursor(-1)
                        self.image.text = self.text
                elif key == K_RETURN:
                    self.submit_text()
                else:
                    self.text = self.text[0:self.cursor_pos] + string + self.text[self.cursor_pos::]
                    self.image.text = self.text
                    self.move_cursor(1)
                return True

    def calc_working_pos(self):
        """Calculate the position of the text cursor - ie, where in the text are we typing... and the text offset."""
        tx, ty = self.pos
        if self.text and self.cursor_pos:
            g1 = self.image.glyphs[0][0][0:self.cursor_pos]
            g2 = self.image.glyphs[0][0][self.cursor_pos+1::]

            w1 = 0
            w2 = 0
            for i in g1:
                w1 += i.get_width()
            for i in g2:
                w2 += i.get_width()

            tp = tx + self.xwidth - w1
            if tp > self.pos[0]:
                tp = self.pos[0]

            cp = tp + w1 - self.cwidth

            return (cp+self.cwidth, ty), (tp+self.cwidth, ty)

        return (tx, ty), (tx+self.cwidth, ty)

    def render(self, offset=(0,0)):
        """Render the Input widget."""
        wpos, tpos = self.calc_working_pos()
        tpx, tpy = tpos
        tpx += offset[0]
        tpy += offset[1]
        self.image.pos = (tpx, tpy)
        view.screen.push_clip2d(self.pos, self.size)
        self.image.render()
        self.image.pos = tpos
        if self.key_active:
            wpx, wpy = wpos
            wpx += offset[0]
            wpy += offset[1]
            self.cursor_image.pos = (wpx, wpy)
            self.cursor_image.render()
            self.cursor_image.pos = wpos
        view.screen.pop_clip()