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

import gnuplot.platforms as gp

_session = gp.Session()

def call(*args):
    for arg in args:
        _session(arg)

def refresh(plot_cmd):
    plot_objects = _session.plot_items
    
    plot_cmds = ", ".join(plot.command for plot in plot_objects)
    
    if _session.debug:
        stderr.write("gnuplot> {} {}\n".format(plot_cmd, plot_cmds))
    
    _session.write(plot_cmd + " " + plot_cmds + "\n")
    
    data = tuple(plot.data for plot in plot_objects
                 if plot.data is not None)
    
    if data:
        _session.write("\ne\n".join(data) + "\ne\n")
        if _session.debug:
            stderr.write("\ne\n".join(data) + "\ne\n")
    
    _session.flush()
    _session.plot_items = []


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

    
def plot_data(*arrays, ltype="points", **kwargs):
    try:
        data = np.vstack(arrays).T
    except TypeError:
        raise DataError("Input arrays should be convertible to a "
                        "numpy array!")
    
    if data.ndim > 2:
        raise DataError("Only 1 or 2 dimensional arrays can be plotted!")
    
    array, text = _convert_data(data, **kwargs)
    
    _session.plot_items.append(PlotDescription(array, text + gp.parse_plot_arguments(**kwargs)))


def plot_grid(data, x=None, y=None, **kwargs):

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
    
    _session.plot_items.append(PlotDescription(array, text + gp.parse_plot_arguments(**kwargs)))


def line(pos, mode, start=0.0, stop=1.0, ref="graph", **kwargs):
    add = gp.parse_kwargs(**kwargs)
    
    if mode == "h" or mode == "horizontal":
        _session("set arrow from {ref} {}, {p} to {ref} {}, {p} nohead {}"
                 .format(start, stop, " ".join(add), p=pos, ref=ref))
    elif mode == "v" or mode == "vertical":
        _session("set arrow from {p}, {ref} {} to {p}, {ref} {} nohead {}"
                 .format(start, stop, " ".join(add), p=pos, ref=ref))
    else:
        raise ValueError('"mode" should be either "h", "horizontal", "v" '
                         'or "vertical"')


def histo(edges, hist, **kwargs):
    title = kwargs.pop("title", None)
    
    edges = edges[:-1] + (edges[1] - edges[0]) / 2.0
    
    vith = "boxes fill solid {}".format(" ".join(gp.parse_kwargs(**kwargs)))
    
    plot_data(edges, hist, title=title, vith=vith)


# TODO: rewrite docs
def plot_file(data, matrix=None, binary=None, array=None, endian="default", **kwargs):
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
    
    if not (isinstance(data, str) or pth.isfile(data)):
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
    
    return PlotDescription(None, text + gp.parse_plot_arguments(**kwargs))


def plot():
    if not _session.silent:
        refresh("plot")

def splot():
    if not _session.silent:
        refresh("splot")


# ***********
# * SETTERS *
# ***********


def debug():
    _session.debug = True

def silent():
    _session.silent = True


def set(name, value):
    if value is True:
        _session("set {}".format(name))
    elif value is False:
        _session("unset {}".format(name))
    else:
        _session("set {} {}".format(name, value))


def size(scale, square=False, ratio=None):
    Cmd = "set size"
    
    if square:
        Cmd += " square"
    else:
        Cmd += " no square"
    
    if ratio is not None:
        Cmd += " ratio {}".format(ratio)
    
    _session("{} {},{}".format(Cmd, scale[0], scale[1]))
    

def palette(pal):
    _session(gp.color_palettes[pal])


def margins(screen=False, **kwargs):
    
    if screen:
        fmt = "set {} at screen {}"
    else:
        fmt = "set {} {}"
    
    for key, value in kwargs.items():
        if key in ("lmargin", "rmargin", "tmargin", "bmargin"):
            _session(fmt.format(key, value))


def multiplot(nplot, **kwargs):
    return gp.MultiPlot(nplot, _session, **kwargs)


def colorbar(cbrange=None, cbtics=None, cbformat=None):
    if cbrange is not None:
        _session("set cbrange [{}:{}]" .format(cbrange[0], cbrange[1]))
    
    if cbtics is not None:
        _session("set cbtics {}".format(cbtics))
    
    if cbformat is not None:
        _session("set format cb '{}'".format(cbformat))
    

def unset_multi(self):
    _session("unset multiplot")
    _session.multi = None


def nicer():
    _session(
    """
    set style line 11 lc rgb 'black' lt 1
    set border 3 back ls 11
    set tics nomirror
    set style line 12 lc rgb 'black' lt 0 lw 1
    set grid back ls 12
    """)
    
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
    
    return colors


def reset():
    _session("reset")


def xtics(*args):
    _session("set xtics {}".format(parse_range(args)))


def ytics(*args):
    _session("set ytics {}".format(parse_range(args)))


def ztics(*args):
    _session("set ztics {}".format(parse_range(args)))


def style(stylenum, ltype, **kwargs):
    """
    Parameters
    ----------
    """
    _session("set style line {} {}".format(stylenum, linedef(ltype, **kwargs)))


def output(outfile, **kwargs):
    term(**kwargs)
    _session("set output '{}'".format(outfile))


def title(title):
    _session('set title "{}"'.format(title))


#def key()

def term(term, **kwargs):
    size     = kwargs.get("size")
    font     = str(kwargs.get("font", "Verdena"))
    fontsize = float(kwargs.get("fontsize", 12))
    enhanced = bool(kwargs.get("enhanced", False))

    txt = "set terminal {}".format(term)
    
    if enhanced:
        txt += " enhanced"
    
    if size is not None:
        _session.size = size
        txt += " size {},{}".format(size[0], size[1])
    
    _session("{} font '{},{}'".format(txt, font, fontsize))


def arrow(From, to, style=None, tag=""):
    temp = "set arrow {} from {},{} to {},{}"\
           .format(tag, From[0], From[1], to[0], to[1])
    
    if style is not None:
        temp += " as {}".format(style)
    
    _session(temp)


def obj(kind):
    pass

# LABELS


def label(definition, position, **kwargs):
    font = str(kwargs.get("font", "Verdena"))
    fontsize = int(kwargs.get("fontsize", 8))
    
    _session("set label '{}' at {},{} font '{}, {}'"
             .format(definition, position[0], position[1], font, fontsize))


def labels(x="x", y="y", z=None):
    _session("set xlabel '{}'".format(x))
    _session("set ylabel '{}'".format(y))
    
    if z is not None:
        _session("set zlabel '{}'".format(z))

def xlabel(xlabel="x"):
    _session("set xlabel '{}'".format(xlabel))

def ylabel(ylabel="y"):
    _session("set ylabel '{}'".format(ylabel))

def zlabel(zlabel="z"):
    _session("set zlabel '{}'".format(zlabel))

# RANGES

def ranges(x=None, y=None, z=None):
    if x is not None and len(x) == 2:
        _session("set xrange [{}:{}]".format(x[0], x[1]))

    if y is not None and len(y) == 2:
        _session("set yrange [{}:{}]".format(y[0], y[1]))

    if z is not None and len(z) == 2:
        _session("set zrange [{}:{}]".format(z[0], z[1]))


def xrange(xmin, xmax):
    _session("set xrange [{}:{}]".format(xmin, xmax))

def yrange(ymin, ymax):
    _session("set yrange [{}:{}]".format(ymin, ymax))

def zrange(zmin, zmax):
    _session("set zrange [{}:{}]".format(zmin, zmax))

def replot():
    _session("replot")


def save(outfile, **kwargs):
    
    # terminal and output cannot be changed in multiplotting
    # if you want to save a multiplot use the output function
    # before defining multiplot
    if _session.multi:
        unset_multi()
    
    output(outfile, **kwargs)
    _session("replot")


def remove_temps():
    for temp in _session.temps:
        remove(temp)
    
    _session.temps = []


class PlotDescription(object):
    def __init__(self, data, command):
        self.data = data
        self.command = command
    
    def __str__(self):
        return "\nData:\n{}\nCommand: {}\n".format(self.data, self.command)

    def __repr__(self):
        return "<PlotDescription data: {} command: {}>".format(self.data, self.command)


# *************************
# * Convenience functions *
# *************************


def arr_bin(array, image=False):
    
    if array.ndim == 1:
        return " binary format='{}'".format(len(array) * gp.fmt_dict[array.dtype])
    elif array.ndim == 2:
        fmt = array.shape[1] * gp.fmt_dict[array.dtype]
        return " binary record={} format='{}'".format(array.shape[0], fmt)


def np2str(array):
    arr_str = np.array2string(array).replace("[", "").replace("]", "")
    
    return "\n".join(line.strip() for line in arr_str.split("\n"))


def linedef(ltype, **kwargs):
    parsed_kwargs = (gp.parse_linedef(key, value)
                     for key, value in kwargs.items())
    
    if ltype is None:
        return " ".join(parsed_kwargs)
    else:
        return "{} {}".format(ltype, " ".join(parsed_kwargs))
    

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
