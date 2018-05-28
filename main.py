import tkinter as tk
import itertools
from screenruler.helpers.conversions import CONVERSIONS


class Popup(tk.Menu):
    def __init__(self, *args, **kwargs):
        """Adapted from http://effbot.org/zone/tkinter-popup-menu.htm"""
        tk.Menu.__init__(self, *args, **kwargs)

    def do_popup(self, event):
        # display the popup menu
        try:
            self.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            # self.grab_release()
            pass


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.dpi = self.winfo_fpixels('1m')
        self.title("Ruler")

        # Define Widgets
        self.frame = tk.Frame(self)
        self.canvas = tk.Canvas(self.frame)
        self.frame.pack(fill='both', expand=True)
        self.canvas.pack(fill='both', expand=True)
        self.canvas['background'] = 'yellow2'

        # Allow user to move window by dragging it
        self.bind("<ButtonPress-1>", self.start_window_move)
        self.bind("<ButtonRelease-1>", self.stop_window_move)
        self.bind("<B1-Motion>", self.on_window_move)

        # Define Dimensions
        self._orient = 'horizontal'  # Orientation of ruler
        self._maxsize = 100  # Width of the ruler
        self._tickside = 'bottom'  # Side of the ruler ticks are drawn on
        self._measure = 'px'  # Measure used by the ruler
        self._measure_tick_positions = {
            'px': [50, 25, 5],
            'pt': [50, 10, 5],
            'em': [5, 1, .5],
            'in': [1, 0.5, 0.1],
            'mm': [10, 5, 1],
            'pi': [6, 3, 1]
        }

        # Create the menu
        self.popup_menu = Popup(self, tearoff=0)
        commands = [
            {"label": "Rotate ↺", "command": self.rotate},
            {"label": "Pixels", "command": lambda *args: self.__dict__.update({"_measure": "px"})},
            {"label": "Points", "command": lambda *args: self.__dict__.update({"_measure": "pt"})},
            {"label": "Em", "command": lambda *args: self.__dict__.update({"_measure": "em"})},
            {"label": "Inches", "command": lambda *args: self.__dict__.update({"_measure": "in"})},
            {"label": "Millimeters", "command": lambda *args: self.__dict__.update({"_measure": "mm"})},
            {"label": "Picas", "command": lambda *args: self.__dict__.update({"_measure": "pi"})}
        ]
        for cmd in commands:
            self.popup_menu.add_command(**cmd)
        self.canvas.bind("<Button-3>", self.popup_menu.do_popup)
        self.after(100, self.step)

    def step(self):
        self.update_dimensions()
        self.canvas.delete('all')
        self.update_orientation()
        self.draw_ticks()
        self.draw_reference_line()
        self.after(50, self.step)

    def update_dimensions(self):
        self._width = self.winfo_width()
        self._height = self.winfo_height()

    def update_orientation(self):
        if self._orient == 'horizontal':
            self.maxsize(100000, self._maxsize)
        elif self._orient == 'vertical':
            self.maxsize(self._maxsize, 100000)
        else:
            raise ValueError("Orientation must be horizontal or vertical")

    def draw_ticks(self):
        # Get span of window in desired unit
        if self._tickside in ('bottom', 'top'):
            span_m = CONVERSIONS['px'][self._measure](self._width)
        else:
            span_m = CONVERSIONS['px'][self._measure](self._height)

        # For each of the offsets draw ticks in the desired positions
        ticks = map(
            lambda m: map(lambda c: m * c, itertools.count()),
            self._measure_tick_positions[self._measure]
        )

        for i, m in enumerate(ticks):
            while True:
                tick = next(m)
                tick_px = int(CONVERSIONS[self._measure]['px'](tick))
                if tick > span_m:
                    break
                if i == 0:
                    self.canvas.create_text(self.tick_coords(tick_px, 30)[:2], text=str(tick))
                    self.canvas.create_line(*self.tick_coords(tick_px, 15))
                elif i == 1:
                    self.canvas.create_line(*self.tick_coords(tick_px, 15))
                elif i == 2:
                    self.canvas.create_line(*self.tick_coords(tick_px, 5))

    def draw_reference_line(self):
        x, y = self.get_mouse_pos()
        if self._orient == "horizontal":
            x1, y1, x2, y2 = self.tick_coords(x, self._height - 20)
            self.canvas.create_line(x1, y1, x2, y2)
            text_offset = -10 if self._tickside == 'bottom' else 10
            self.canvas.create_text(
                x1, y1 + text_offset,
                text="{:.2f} {}".format(float(CONVERSIONS['px'][self._measure](x)), self._measure)
            )
        else:
            x1, y1, x2, y2 = self.tick_coords(y, self._width)
            self.canvas.create_line(x1, y1, x2, y2)
            self.canvas.create_text(
                0 if self._tickside == 'right' else self._width,
                y1 - 10,
                text="{:.2f} {}".format(float(CONVERSIONS['px'][self._measure](y)), self._measure),
                anchor='e' if self._tickside == 'left' else 'w'
            )

    def tick_coords(self, m, d):
        """
        Returns px coordinates for ticks drawn on the canvas.
        :param m: Measure the tick represents (m=6 for the 6px tick)
        :param d: Offset in px for the inside end of the tick
        :return: (x1, y1, x2, y2)
        """
        coords = {
            'bottom': (m, self._height - d, m, self._height),
            'top': (m, d, m, 0),
            'right': (self._width - d, m, self._width, m),
            'left': (d, m, 0, m),
        }
        return coords[self._tickside]

    def get_mouse_pos(self):
        abs_coord_x = self.winfo_pointerx() - self.winfo_rootx()
        abs_coord_y = self.winfo_pointery() - self.winfo_rooty()
        return abs_coord_x, abs_coord_y

    def rotate(self):
        w, h = self._height, self._width
        self._tickside = {"bottom": "right", "right": "top", "top": "left", "left": "bottom"}[self._tickside]
        self._orient = {"bottom": "horizontal", "right": "vertical", "top": "horizontal", "left": "vertical"}
        self._orient = self._orient[self._tickside]
        self.maxsize(10000, 10000)
        self.geometry("%dx%d"%(w, h))
        self.update_idletasks()

    # https://stackoverflow.com/questions/4055267/python-tkinter-mouse-drag-a-window-without-borders-eg-overridedirect1
    def start_window_move(self, event):
        self._x = event.x
        self._y = event.y

    def stop_window_move(self, event):
        self._x = None
        self._y = None

    def on_window_move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))


app = App()
app.mainloop()
