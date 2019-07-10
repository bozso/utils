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
from os import fdopen
from sys import stderr, platform
from atexit import register
import subprocess as sub

from .private import color_palettes

__all__ = (
    "arrow", "call", "colorbar", "debug", "histo", "label", "labels",
    "line", "linedef", "margins", "multiplot", "obj",
    "output", "palette", "plot", "data", "file", "grid",
    "ranges", "refresh", "replot", "reset", "save",
    "set", "silent", "splot", "style", "term", "title", "unset_multi",
    "xlabel", "xrange", "xtics", "ylabel", "yrange", "ytics",
    "zlabel", "zrange", "ztics", "colors", "dollar", 
    "zero", "one", "two", "three", "x", "y", "Symbol"
)


config = {
    "persist": False,
    "debug": False,
    "silent": False,
    "exe": "gnuplot",
    "size": (800, 600),
    "startup": 
    """
    set style line 11 lc rgb 'black' lt 1
    set border 3 back ls 11
    set tics nomirror
    set style line 12 lc rgb 'black' lt 0 lw 1
    set grid back ls 12
    """
}


process, multi, debug, silent, plot_items = \
None, None, config["debug"], config["silent"], []


def startup():
    global process
    
    if config["persist"]:
        cmd = [config["exe"], "--persist"]
    else:
        cmd = [config["exe"]]
        
    process = sub.Popen(cmd, stderr=sub.STDOUT, stdin=sub.PIPE)


startup()

def close():
    global process
    if multi is not None:
        call("unset multiplot")
    
    if process is not None:
        process.stdin.close()
        retcode = process.wait()
        process = None


register(close)
    
write = process.stdin.write
flush = process.stdin.flush


def call(*commands):
    global debug
    
    for command in commands:
        if debug:
            stderr.write("gnuplot> %s\n" % command)
        
        write(bytes(b"%s\n" % bytes(command, encoding='utf8')))
        flush()

call(config["startup"])


def refresh(plot_cmd):
    global plot_items
    plot_cmds = ", ".join(plot.command for plot in plot_items)
    
    if debug:
        stderr.write("gnuplot> %s %s\n" % (plot_cmd, plot_cmds))
    
    call(plot_cmd + " " + plot_cmds + "\n")
    
    data = tuple(plot.data for plot in plot_items
                 if plot.data is not None)
    
    if data:
        write("\ne\n".join(data) + "\ne\n")
        
        if debug:
            stderr.write("\ne\n".join(data) + "\ne\n")
    
    flush()
    plot_items = []


def data(*arrays, ltype="points", **kwargs):
    try:
        data = np.vstack(arrays).T
    except TypeError:
        raise DataError("Input arrays should be convertible to a "
                        "numpy array!")
    
    if data.ndim > 2:
        raise DataError("Only 1 or 2 dimensional arrays can be plotted!")
    
    array, text = _convert_data(data, **kwargs)
    
    plot_items.append(PlotDescription(array, text, **kwargs))


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
    
    array, text = _convert_data(grid, grid=True, **kwargs)
    
    plot_items.append(PlotDescription(array, text, **kwargs))


def line(pos, mode, start=0.0, stop=1.0, ref="graph", **kwargs):
    add = gp.parse_kwargs(**kwargs)
    
    if mode == "h" or mode == "horizontal":
        call("set arrow from {ref} {}, {p} to {ref} {}, {p} nohead {}"
             .format(start, stop, " ".join(add), p=pos, ref=ref))
    elif mode == "v" or mode == "vertical":
        call("set arrow from {p}, {ref} {} to {p}, {ref} {} nohead {}"
             .format(start, stop, " ".join(add), p=pos, ref=ref))
    else:
        raise ValueError('"mode" should be either "h", "horizontal", "v" '
                         'or "vertical"')


def histo(edges, hist, **kwargs):
    edges = edges[:-1] + (edges[1] - edges[0]) / 2.0
    
    vith = "boxes fill solid {}".format(" ".join(gp.parse_kwargs(**kwargs)))
    
    data(edges, hist, vith=vith, **kwargs)


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
    
    plot_items.append(PlotDescription(None, text, **kwargs))


def plot():
    if not silent:
        refresh("plot")

def splot():
    if not silent:
        refresh("splot")


def _convert_data(data, grid=False, **kwargs):
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
        
        _session.temps.append(filename)
        
        text  = "'{}'".format(filename)
        array = None
    
    return array, text + add


def set(**kwargs):
    call(";".join(parse_set(key, value) for key, value in kwargs.items()))


def size(scale, square=False, ratio=None):
    Cmd = "set size"
    
    if square:
        Cmd += " square"
    else:
        Cmd += " no square"
    
    if ratio is not None:
        Cmd += " ratio {}".format(ratio)
    
    call("{} {},{}".format(Cmd, scale[0], scale[1]))
    

def palette(pal):
    call(color_palettes[pal])


def margins(screen=False, **kwargs):
    
    if screen:
        fmt = "set {} at screen {}"
    else:
        fmt = "set {} {}"
    
    for key, value in kwargs.items():
        if key in ("lmargin", "rmargin", "tmargin", "bmargin"):
            call(fmt.format(key, value))


def multiplot(nplot, **kwargs):
    raise NotImplemented("Multiplot functionality still in the works.")
#     return gp.MultiPlot(nplot, _session, **kwargs)


def colorbar(cbrange=None, cbtics=None, cbformat=None):
    if cbrange is not None:
        call("set cbrange [%f:%s]"  % (cbrange[0], cbrange[1]))
    
    if cbtics is not None:
        call("set cbtics %s" % (cbtics))
    
    if cbformat is not None:
        call("set format cb '%s'" % (cbformat))
    

def unset_multi():
    call("unset multiplot")
    multi = None


def reset():
    call("reset")


def xtics(*args):
    call("set xtics %s" % (parse_range(args)))


def ytics(*args):
    call("set ytics %s" % (parse_range(args)))


def ztics(*args):
    call("set ztics %s" % (parse_range(args)))


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
    call('set title "%s"' % (title))


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
    temp = "set arrow %s from %f,%f to %f,%f"\
           .format(tag, From[0], From[1], to[0], to[1])
    
    if style is not None:
        temp += " as %s".format(style)
    
    call(temp)


def obj(kind):
    pass


def label(definition, position, **kwargs):
    font = str(kwargs.get("font", "Verdena"))
    fontsize = int(kwargs.get("fontsize", 8))
    
    call("set label '%s' at %f,%f font '%s, %d'"
         % (definition, position[0], position[1], font, fontsize))


def labels(x="x", y="y", z=None):
    call("set xlabel '%s'" % (x))
    call("set ylabel '%s'" % (y))
    
    
    if z is not None:
        call("set zlabel '%s'" % (z))


def xlabel(label="x"):
    call("set xlabel '%s'" % (label))

def ylabel(label="y"):
    call("set ylabel '%s'" % (label))

def zlabel(label="z"):
    call("set zlabel '%s'" % (label))


def ranges(x=None, y=None, z=None):
    if x is not None and len(x) == 2:
        call("set xrange [%f:%f]" % (x[0], x[1]))

    if y is not None and len(y) == 2:
        call("set yrange [%f:%f]" % (y[0], y[1]))

    if z is not None and len(z) == 2:
        call("set zrange [%f:%f]" % (z[0], z[1]))


def xrange(min, max):
    call("set xrange [%f:%f]" % (min, max))


def yrange(min, max):
    call("set yrange [%f:%f]" % (min, max))

def zrange(min, max):
    call("set zrange [%f:%f]" % (min, max))


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


zero, one, two, three, x, y = \
dollar(0), dollar(1), dollar(2), dollar(3), Symbol("x"), Symbol("y")


class PlotDescription(object):
    def __init__(self, data, command, **kwargs):
        self.data = data
        self.command = command + parse_plot_arguments(**kwargs)
    
    def __str__(self):
        return "\nData:\n{}\nCommand: {}\n".format(self.data, self.command)

    def __repr__(self):
        return "<PlotDescription data: {} command: {}>".format(self.data, self.command)


# *************************
# * Convenience functions *
# *************************


def arr_bin(array, image=False):
    
    if array.ndim == 1:
        return " binary format='%s'" % (len(array) * gp.fmt_dict[array.dtype])
    elif array.ndim == 2:
        fmt = array.shape[1] * gp.fmt_dict[array.dtype]
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


def parse_linedef(key, value):
    
    if key == "pt" or key == "pointtype":
        return "%s %s" % (key, point_type_dict[value])
    elif key == "lt" or key == "linetype":
        return "%s %s" % (key, line_type_dict[value])
    elif key == "rgb":
        return "lc %s '%s'".format(key, value)
    
    if isinstance(value, bool) and value:
        return key
    elif isinstance(value, str):
        return "%s '%s'" % (key, value)
    else:
        return "%s %s" % (key, value)


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
    
    
    if vith is not None:
        text = "%s with %s" % (text, vith)
    else:
        add = (parse_linedef(key, value) for key, value in kwargs.items())
        text = "%s with %s %s" % (text, ptype, " ".join(add))
    
    return text


def proc_using(txt):
    if "$" in txt:
        return "(%s)" % txt
    else:
        return txt


def parse_set(name, value):
    if value is True:
        return "set {}".format(name)
    elif value is False:
        return "unset {}".format(name)
    else:
        return "set {} {}".format(name, value)

        
point_type_dict = {
    "dot": 0,
    "+": 1,
    "x": 2,
    "+x": 3,
    "empty_square": 4,
    "filed_square": 5,
    "empty_circle": 6,
    "o": 6,
    "filled_circle": 7,
    "empty_up_triangle": 8,
    "filled_up_triangle": 9,
    "empty_down_triangle": 10,
    "filled_down_triangle": 11,
    "empty_rombus": 12,
    "filled_rombus": 13,
}


line_type_dict = {
    "black": -1,
    "dashed": 0,
    "red": 1,
    "green": 2,
    "blue": 3,
    "purple": 4,
    "teal": 5,
}


colors = {
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


# **************
# * Exceptions *
# **************

class GnuplotError(Exception):
    pass

class OptionError(GnuplotError):
    """Raised for unrecognized or wrong option(s)"""
    pass


class DataError(GnuplotError):
    """Raised for data in the wrong format"""
    pass
