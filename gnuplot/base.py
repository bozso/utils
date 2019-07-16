# Copyright (C) 2018  István Bozsó
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import os.path as pth
import numpy as np

from builtins import str
from numbers import Number
from tempfile import mkstemp
from os import fdopen, path as pth
from sys import stderr, platform
from atexit import register
import subprocess as sub
from tempfile import _get_default_tempdir, _get_candidate_names
from time import sleep

try:
    from IPython.display import Image, display
except ImportError:
    Image = None


from .config import *

print()

__all__ = (
    "arrow", "call", "colorbar", "histo", "label", "line", "linedef",
    "margins", "multiplot", "obj", "output", "palette", "plot", "data",
    "file", "grid", "refresh", "replot", "reset", "save", "set", "silent",
    "splot", "style", "term", "title", "unset_multi", "colors",
    "x", "y", "z", "sym", "col", "update", "points", "lines"
)

# TODO:
# set commands should come after set out and set term
# 


tmp_path = _get_default_tempdir()

def get_tmp(path=tmp_path):
    return pth.join(path, next(_get_candidate_names()))


def update(**kwargs):
    config.update(kwargs)

    
class Gnuplot(object):
    def __init__(self):
        self.multi = self.process = None
        
        if config["persist"]:
            cmd = [config["exe"], "--persist"]
        else:
            cmd = [config["exe"]]
        
        self.process = sub.Popen(cmd, stderr=sub.STDOUT, stdin=sub.PIPE)
        
        self.write, self.flush, self.set_commands = \
        self.process.stdin.write, self.process.stdin.flush, []
        
    
    def __del__(self):
        if self.multi is not None:
            self("unset multiplot")
        
        process = self.process
        
        if process is not None:
            process.stdin.close()
            retcode = process.wait()
            self.process = None
    
    
    def __call__(self, *commands):
        debug, write, flush = config["debug"], self.write, self.flush
        
        for command in commands:
            if debug:
                stderr.write("gnuplot> %s\n" % command)
            
            write(bytes(b"%s\n" % bytes(command, encoding='utf8')))
            flush()
    
    
    def refresh(self, plot_cmd, *items):
        plot_cmds = ", ".join(plot.command for plot in items)
        
        assert len({item.ptype for item in items}) == 1
        
        ptype = items[0].ptype
        
        self("; ".join(cmd for cmd in self.set_commands))
        self("; ".join(config[ptype]))
        
        self.set_commands = []
        self(plot_cmd + " " + plot_cmds + "\n")
        
        data = tuple(plot.data for plot in items
                     if plot.data is not None)
        
        if data:
            self.write("\ne\n".join(data) + "\ne\n")
            
            if debug:
                stderr.write("\ne\n".join(data) + "\ne\n")
        
        self.flush()


class Axis(object):
    def __init__(self, call, name="x"):
        self.call, self.name, self._range, self._label = \
        call, name, [], None
    
    def __getitem__(self, k):
        if isinstance(k, slice):
            set(**{"%stics" % self.name: "%f,%f,%f" 
                                         % (k.start, k.step, k.stop)})
    
    def set_range(self, _range):
        self._range = _range
        set(**{"%srange" % self.name: "[%f:%f]" % (_range[0], _range[1])})
    
    def get_range(self):
        return self._range
    
    range = property(get_range, set_range)
    
    
    def set_label(self, label):
        self._label = label
        set(**{"%slabel" % self.name: "'%s'" % label})

    
    def get_label(self):
        return self._label
    
    label = property(get_label, set_label)
    
    
    def get_format(self):
        return self._format
    
    def set_format(self, format):
        self._format = format
        set(**{"format %s" % self.name: "'%s'" % format})
    
    format = property(get_format, set_format)
    

session = Gnuplot()

call, flush, refresh = session.__call__, session.flush, session.refresh
silent = config["silent"]


def set(**kwargs):
    session.set_commands.extend(parse_set(key, value)
                                for key, value in kwargs.items())

# TODO: properly provide access to debug
# debug = property(session.get_debug, session.set_debug)


x = Axis(call, "x")
y = Axis(call, "y")
z = Axis(call, "z")


def data(*arrays, ltype="points", **kwargs):
    try:
        data = np.vstack(arrays).T
    except TypeError:
        raise DataError("Input arrays should be convertible to a "
                        "numpy array!")
    
    if data.ndim > 2:
        raise DataError("Only 1 or 2 dimensional arrays can be plotted!")
    
    array, text = convert_data(data, **kwargs)
    
    return PlotDescription(array, text, "2D", **kwargs)


def grid(data, x=None, y=None, **kwargs):

    data = np.asarray(data, np.float32)
    
    try:
        (rows, cols) = data.shape
    except ValueError:
        raise DataError("data array must be 2-dimensional!")
    
    if x is None:
        x = np.arange(cols)
    else:
        x = np.array(x, dtype=np.float32)
        
        if x.shape != (cols,):
            raise DataError("x should have number of elements equal to "
                            "the number of columns of data!")

    if y is None:
        y = np.arange(rows)
    else:
        y = np.array(y, dtype=np.float32)
        
        if y.shape != (rows,):
            raise DataError("y should have number of elements equal to "
                            "the number of rows of data!")
        
    grid        = np.zeros((rows + 1, cols + 1), np.float32)
    grid[0,0]   = cols
    grid[0,1:]  = x
    grid[1:,0]  = y
    grid[1:,1:] = data.astype(np.float32)
    
    array, text = convert_data(grid, grid=True, **kwargs)
    
    return PlotDescription(array, text, "3D", **kwargs)


def line(pos, mode, start=0.0, stop=1.0, ref="graph", **kwargs):
    add = gp.parse_kwargs(**kwargs)
    
    if mode == "h" or mode == "horizontal":
        tpl = "from {ref} {}, {p} to {ref} {}, {p} nohead {}"
    elif mode == "v" or mode == "vertical":
        tpl = "from {p}, {ref} {} to {p}, {ref} {} nohead {}"
    else:
        raise ValueError('"mode" should be either "h", "horizontal", "v" '
                         'or "vertical"')

    set(arrow=tpl.format(start, stop, " ".join(add), p=pos, ref=ref))

    
def histo(edges, hist, **kwargs):
    edges = edges[:-1] + (edges[1] - edges[0]) / 2.0
    
    vith = "boxes fill solid %s" % (" ".join(gp.parse_kwargs(**kwargs)))
    
    return data(edges, hist, vith=vith, **kwargs)


# TODO: rewrite docs
def file(data, matrix=None, binary=None, array=None, endian="default",
         **kwargs):
    """
    DOCUMENTATION NEEDS TO BE REWORKED!
    Sets the text to be used for the 'plot' command of Gnuplot for
    plotting (x,y) data pairs of a file.
    
    Parameters
    ----------
    data : str
        Path to data file.
    pt_type : str, optional
        The symbol used to plot (x,y) data pairs. Default is "circ" (filled
        circles). Selectable values:
            - "circ": filled circles
    pt_size : float, optional
        Size of the plotted symbols. Default value 1.0 .
    line_type : str, optional
        The line type used to plot (x,y) data pairs. Default is "circ"
        (filled circles). Selectable values:
            - "circ": filled circles
    line_width : float, optional
        Width of the plotted lines. Default value 1.0 .
    line_style : int, optional
        Selects a previously defined linestyle for plotting the (x,y) data
        pairs. You can define linestyle with gnuplot.style .
        Default is None.
    title : str, optional
        Title of the plotted datapoints. None (= no title given)
        by default.
    **kwargs
        Additional arguments: index, every, using, smooth, axes.
        See Gnuplot docuemntation for the descritpion of these
        parameters.
    
    Returns
    -------
    cmd: str
    
    Examples
    --------
    
    >>> from gnuplot import Gnuplot
    >>> g = Gnuplot(persist=True)
    >>> g.plot("data1.txt", title="Example plot 1")
    >>> g.plot("data2.txt", title="Example plot 2")
    >>> del g
    
    """
    
    if not pth.isfile(data):
        raise ValueError("data should be a string path to a data file!")
    
    text = "'{}'".format(data)

    if binary is not None and not isinstance(binary, bool):
        if array is not None:
            text += " binary array={} format='{}' "\
                    "endian={}".format(array, binary, endian)
        else:
            text += " binary format='{}' endian={}"\
                    .format(binary, endian)
    elif binary:
        text += " binary"
    
    return PlotDescription(None, text, **kwargs)


def plot_ipython(plot_cmd, *items, **kwargs):
    if Image is not None:
        tmp = get_tmp() + ".png"
        
        kwargs.setdefault("term", "pngcairo")
        output(tmp, **kwargs)
        
        if not silent:
            refresh(plot_cmd, *items)
        
        # safety waiting time
        sleep(1.0)
        
        display(Image(filename=tmp))
        
        return tmp
    elif not silent:
        refresh(plot_cmd, *items)
    
    
def plot(*items, **kwargs):
    return plot_ipython("plot", *items, **kwargs)

def splot(*items, **kwargs):
    return plot_ipython("splot", *items, **kwargs)


def convert_data(data, grid=False, **kwargs):
    binary = bool(kwargs.get("binary", True))
    inline = bool(kwargs.get("inline", False))

    if inline and binary:
        raise OptionError("Inline binary format is not supported!")
    
    if binary:
        content = data.tobytes()
        mode = "wb"
        
        if grid:
            add = " binary matrix"
        else:
            add = arr_bin(data)
    else:
        content = np2str(data)
        mode = "w"
        
        if grid:
            add = " matrix"
        else:
            add = ""
    
    if inline:
        text  = "'-'"
        array = content
    else:
        fd, filename, = mkstemp(text=True)

        f = fdopen(fd, mode)
        f.write(content)
        f.close()
        
        text  = "'{}'".format(filename)
        array = None
    
    return array, text + add


def size(scale, square=False, ratio=None):
    Cmd = ""
    
    if square:
        Cmd += " square"
    else:
        Cmd += " no square"
    
    if ratio is not None:
        Cmd += " ratio %f" % (ratio)
    
    set(size="%s %f %f" % (Cmd, scale[0], scale[1]))
    

def palette(pal):
    call(color_palettes[pal])


def margins(screen=False, **kwargs):
    fmt = "at screen %f" if screen else "%s"
    
    set(**{key: fmt % value
           for key, value in kwargs.items()
           if key in {"lmargin", "rmargin", "tmargin", "bmargin"}})


def multiplot(nplot, **kwargs):
    raise NotImplemented("Multiplot functionality still in the works.")
#     return gp.MultiPlot(nplot, _session, **kwargs)


def colorbar(cbrange=None, cbtics=None, cbformat=None):
    if cbrange is not None:
        set(cbrange="[%f:%f]" % (cbrange[0], cbrange[1]))
    
    if cbtics is not None:
        set(cbtics=cbtics)
    
    if cbformat is not None:
        set(**{"format cb": cbformat})
    

def unset_multi():
    call("unset multiplot")
    multi = None


def reset():
    call("reset")


def style(stylenum, ltype, **kwargs):
    """
    Parameters
    ----------
    """
    call("set style line %d %s" % (stylenum, linedef(ltype, **kwargs)))


def output(outfile, **kwargs):
    term(**kwargs)
    call("set output '%s'" % (outfile))


def title(title):
    set(title=title)


def term(term, **kwargs):
    size     = kwargs.get("size")
    font     = str(kwargs.get("font", "Verdena"))
    fontsize = float(kwargs.get("fontsize", 12))
    enhanced = bool(kwargs.get("enhanced", False))

    txt = "set terminal %s" % (term)
    
    if enhanced:
        txt += " enhanced"
    
    if size is not None:
        txt += " size %d,%d" % (size[0], size[1])
    
    call("%s font '%s,%f'" % (txt, font, fontsize))


def arrow(From, to, style=None, tag=""):
    temp = "%s from %f,%f to %f,%f" % (tag, From[0], From[1], to[0], to[1])
    
    if style is not None:
        temp += " as %s" % (style)
    
    set(arrow=temp)


def obj(kind):
    pass


def label(definition, position, **kwargs):
    font = str(kwargs.get("font", "Verdena"))
    fontsize = int(kwargs.get("fontsize", 8))
    
    set(label="'%s' at %f,%f font '%s, %d'"
        % (definition, position[0], position[1], font, fontsize))


def replot():
    call("replot")


def save(outfile, **kwargs):
    
    # terminal and output cannot be changed in multiplotting
    # if you want to save a multiplot use the output function
    # before defining multiplot
    unset_multi()
    
    output(outfile, **kwargs)
    call("replot")


def make_operator(symbol):
    tpl = "(%s {} %s)".format(operators[symbol])
    
    if symbol.startswith("r"):
        def f(self, other):
            return Symbol(tpl % (other, self))
    else:
        def f(self, other):
            return Symbol(tpl % (self, other))
        
    return f

    
operators = {
    "add": "+", "radd": "+",
    "sub": "-", "rsub": "-",
    "mul": "*", "rmul": "*",
    "div": "/", "rdiv": "/",
    "truediv": "/", "rtruediv": "/",
    "pow": "^", "rpow": "^",
    "lt" : "<", "le" : "<=",
    "gt" : ">", "ge" : ">="
}



Symbol = type("Symbol", (str,), {"__%s__" % op: make_operator(op)
                                 for op in operators.keys()})

def dollar(num):
    return Symbol("$%d" % num)


class Dollar(object):
    cache = {num: dollar(num) for num in range(11)}
    
    def __getitem__(self, num):
        cache = Dollar.cache
        if num in cache:
            return cache[num]
        else:
            tmp = dollar(num)
            cache[num] = tmp
            return tmp

col = Dollar()

sym = type("Symbols", (object,), {
    "x": Symbol("x"), 
    "y": Symbol("y")
})


class PlotDescription(object):
    def __init__(self, data, command, ptype, **kwargs):
        self.data, self.ptype, self.command = \
        data, ptype, command + parse_plot_arguments(**kwargs)
    
    def __str__(self):
        return self.command

    
    def __repr__(self):
        return "<PlotDescription data: %s, command: %s>" \
                % (self.data, self.command)


# *************************
# * Convenience functions *
# *************************


def arr_bin(array, image=False):
    if array.ndim == 1:
        return " binary format='%s'" % (len(array) * gp.fmt_dict[array.dtype])
    elif array.ndim == 2:
        fmt = array.shape[1] * fmt_dict[array.dtype]
        return " binary record=%d format='%s'" % (array.shape[0], fmt)


def np2str(array):
    arr_str = np.array2string(array).replace("[", "").replace("]", "")
    
    return "\n".join(line.strip() for line in arr_str.split("\n"))


def linedef(ltype, **kwargs):
    parsed_kwargs = (parse_linedef(key, value)
                     for key, value in kwargs.items())
    
    if ltype is None:
        return " ".join(parsed_kwargs)
    else:
        return "%s %s" % (ltype, " ".join(parsed_kwargs))


def points(**kwargs):
    return linedef("points", **kwargs)
        
        
def lines(**kwargs):
    return linedef("lines", **kwargs)


def parse_linedef(key, value):
    if key == "pt" or key == "pointtype":
        return "%s %s" % (key, point_type_dict[value])
    elif key == "lt" or key == "linetype":
        return "%s %s" % (key, line_type_dict[value])
    elif key == "rgb":
        return "lc %s '%s'".format(key, value)
    
    if isinstance(value, bool) and value:
        return key
    elif isinstance(value, float):
        return "%s %f" % (key, value)
    elif isinstance(value, int):
        return "%s %d" % (key, value)
    else:
        return parse_option(key, value)


def parse_plot_arguments(**kwargs):
    vith, using, ptype, title = \
    kwargs.pop("vith", None), kwargs.pop("using", None), \
    kwargs.pop("ptype", "points"), kwargs.pop("title", None)
    
    text = ""
    
    if using is not None:
        if isinstance(using, tuple):
            text = "%s using %s:%s" \
                   % (text, proc_using(using[0]), proc_using(using[1]))
        else:
            text = "%s using (%s)" % (text, proc_using(using))
    
    
    if title is None:
        text += " notitle"
    else:
        text += " title '%s'" % (title)
    
    if vith is None:
        add = (parse_linedef(key, value) for key, value in kwargs.items())
        text = "%s with %s %s" % (text, ptype, " ".join(add))
    elif vith is not None:
        text = "%s with %s" % (text, vith)
    
    return text



def parse_range(args):
    if len(args) == 1:
        return str(args[0])
    else:
        return "(%s)" % (", ".join(str(elem) for elem in args))


quoted = frozenset({
    "format",
    "clabel",
    "missing",
    "separator",
    "locale",
    "rgb",
    "rgbcolor"
})


equaled = frozenset({
    "format",
    "filetype"
})


def parse_option(key, value):
    qtd, eqd = key in quoted, key in equaled
    
    if qtd and eqd:
        return "%s='%s'" % (key, value)
    elif qtd:
        return "%s '%s'" % (key, value)
    elif eqd:
        return "%s=%s" % (key, value)
    else:
        return "%s %s" % (key, value)


def proc_using(txt):
    if "$" in txt:
        return "(%s)" % txt
    else:
        return txt


def parse_set(key, value):
    if value is True:
        return "set %s" % (key)
    elif value is False:
        return "unset %s" % (key)
    else:
        return "set %s" % parse_option(key, value)


color_codes = {
    "red": "#8b1a0e",
    "green": "#5e9c36",
    "lightgreen": "#4d9178",
    "blue": "#0074D9",
    "darkblue": "#140a60",
    "navy": "#001f3f",
    "aqua": "#7FDBFF",
    "teal": "#39CCCC",
    "olive": "#3D9970",
    "yellow" :"#FFDC00",
    "lime" :"#01FF70",
    "orange": "#FF851B",
    "maroon": "#85144b",
    "fuchsia": "#F012BE",
    "purple": "#B10DC9",
    "black": "#111111",
    "gray": "#AAAAAA",
    "silver": "#DDDDDD"
}


colors = type("Colors", (object,), color_codes)
