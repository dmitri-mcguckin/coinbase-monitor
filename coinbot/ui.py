import urwid
from . import APP_NAME, APP_VERSION


class PriceModel:
    def __init__(self):
        self.data = [20, 40, 33, 10, 22]


class PriceGraphView():
    palette = [
        ('body', 'black', 'light gray', 'standout'),
        ('header', 'white', 'dark red',  'bold'),
        ('screen edge', 'light blue', 'dark cyan'),
        ('main shadow', 'dark gray', 'black'),
        ('line', 'black', 'light gray', 'standout'),
        ('bg background', 'light gray', 'black'),
        ('bg 1', 'black', 'dark blue', 'standout'),
        ('bg 1 smooth', 'dark blue', 'black'),
        ('bg 2', 'black', 'dark cyan', 'standout'),
        ('bg 2 smooth', 'dark cyan', 'black'),
        ('button normal', 'light gray', 'dark blue', 'standout'),
        ('button select', 'white', 'dark green'),
        ('line', 'black', 'light gray', 'standout'),
        ('pg normal', 'white', 'black', 'standout'),
        ('pg complete', 'white', 'dark magenta'),
        ('pg smooth', 'dark magenta', 'black')
    ]

    samples_per_bar = 10
    num_bars = 5
    offset_per_sec = 10

    def __init__(self, controller):
        self.controller = controller
        urwid.WidgetWrap.__init__(self, self.main_window())

    def bar_graph(self):
        return urwid.BarGraph(['bg background', 'bg 1', 'bg 2'])


def exit(button: urwid.Button):
    raise urwid.ExitMainLoop()


def ui():
    # Styling
    palette = [
        ('exit', 'black', 'light red')
    ]

    # Elements
    graph = urwid.BarGraph(['bg background', 'bg 1', 'bg 2'])
    graph.set_bar_width(1)
    graph.set_data([(10, 100, 20)], 150)
    gwrap = urwid.WidgetWrap(graph)
    col_1 = urwid.LineBox(gwrap)

    cols = urwid.Columns([col_1])

    # content = urwid.Padding(urwid.Filler(cols, 'top'), 'right')
    border = urwid.LineBox(cols,
                           title=f'{APP_NAME} v{APP_VERSION}',
                           title_align='left')

    # Loop Stuff
    loop = urwid.MainLoop(border, palette)
    loop.run()
