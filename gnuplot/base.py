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

from os import mkdir
from builtins import str
from numbers import Number
from tempfile import mkstemp
from os import fdopen, path as pth
from sys import stderr, platform
from atexit import register
import subprocess as sub
from tempfile import _get_default_tempdir, _get_candidate_names
from time import sleep
from shlex import split
from sys import maxsize
from functools import partial
from hashlib import sha224
from collections import namedtuple
from shutil import move
from itertools import tee, takewhile, islice, chain, filterfalse

try:
    from IPython.display import Image, display
except ImportError:
    Image = None

from utils import *


config = {
    "persist": False,
    "debug": False,
    "silent": False,
    "exe": "gnuplot",
    "size": (800, 600),
    
    "2D":
    """
    set style line 11 lc rgb 'black' lt 1
    set border 3 back ls 11 lw 2.5
    set tics nomirror
    set style line 12 lc rgb 'black' lt 0 lw 1
    set grid back ls 12 lw 2.0
    """,
    
    "3D":
    """
    set style line 11 lc rgb 'black' lt 1
    set border 3 back ls 11 lw 2.5
    set tics nomirror
    set style line 12 lc rgb 'black' lt 0 lw 1
    set grid back ls 12 lw 2.0
    """
}

    

tmp_path = pth.join(_get_default_tempdir(), "gnuplot")
data_path = pth.join(tmp_path, "data")
gp_path = pth.join(tmp_path, "tmp.gp")


if not pth.isdir(tmp_path):
    mkdir(tmp_path)

if not pth.isdir(data_path):
    mkdir(data_path)


def phash(data):
    return sha224(data).hexdigest()

    
def phash_arr(*items):
    return phash(item.dump() for item in items)
    
    
def update(**kwargs):
    config.update(kwargs)


def make_property(name):
    mangled = "_%s" % name
    
    def setter(self, val):
        setattr(self, mangled, val)
    
    def getter(self):
        return getattr(self, mangled)

    return property(getter, setter)


def number(item):
    if not isinstance(item, Number):
        raise TypeError("Expected a number got %s" % (item))
    
    return str(item)
    
    
def numbers(item, ntype, brackets=False):
    if not isinstance(item iterable):
        raise TypeError("Expected an iterable %s" % (item))
    
    numbers = (number(elem) for elem in item)
    
    if ntype == "range":
        ret = ":".join(numbers)
    elif ntype == "tuple":
        ret = ",".join(numbers)
    elif ntype == 
    
    
    if brackets == "square":
        ret = "[%s]" % ret
    elif brackets == "curly":
        ret = "{%s}" % ret
    elif brackets == "round":
        ret = "(%s)" % ret
    
    return ret
    

def string(item, quoted=True):
    if quoted:
        return '"%s"' % str(item)
    else:
        return str(item)

label = partial(string, quoted=False)

def labels(item):
    if not isinstance(item iterable):
        raise TypeError("Expected an iterable %s" % (item))
    
    labels = (label(elem) for elem in item)
    
    return ",".join(labels)
    




class Options(object):
    __slots__ = ("prefix",)
    
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", None)
        prefix = kwargs.pop("prefix", None)
        
        assert prefix is not None
        
        if name is not None:
            self.prefix = "%s%s" % (name, prefix)
        else:
            self.prefix = prefix
        
        for key, val in self.options.items():
            setattr(self, key, kwargs.get(key, val))
    
    
    def __getattr__(self, item):
        assert item in self.__slots__
    
def make_property(name, validator):
    mangled = "_%s" % name
    
    def getter(self):
        return getattr(self, mangled)
    
    def setter(self, item):
        setattr(self, mangled, validator(item))
    
    return property(getter, setter)


def properties(cls):
    options = cls.__options__
    attribs = options.attribs
    names = tuple(attribs.keys())
    cname = cls.__name__
    
    prefix = options.prefix
    
    nt = new_type(cname, names)
    
    
    
    def iter(self):
        for key in names:
            yield key, getattr(self, key)
    
    def tostring(self):
        return "%s(%s)" % (cname, 
               "; ".join("%s: %s" % (key, val) for key, val in self))
    
    def parse(self):
        prefix = self.prefix
        
        return "\n".join(parse_set(key, val, prefix)
                         for key, val in self
                         if val is not None)
    
    if hasattr(cls, "__slots__"):
        mangled += getattr(cls, "__slots__")
    
    nt.update({
        "__init__": init,
        "__slots__": names + ("prefix",),
        "__str__": tostring,
        "__iter__": iter,
        "parse": parse
        # "prefix": prefix
        # "__options__": cls.options,
        # "__option_names__": tuple(cls.options.keys()),
    })
    
    
    for key, val in attribs.items():
        callables[key] = make_property(key)
    
    return type(cname, (object,), callables)


_options = new_type("Options", ("prefix", "attribs"))


def options(prefix=None, **kwargs):
    return _options(prefix, kwargs)


@properties
class Tics:
    __options__ = options(prefix="tics",
        format=None,
        axis=None
    )
    

fslots = ("multi", "cmd", "datafile", "global_sets", "sets", "commands",
          "ext", "palette", "count")

axes = {"x", "y", "x2", "y2", "cb"}

fslots += tuple("%stics" % name for name in axes)


class Figure(object):
    __slots__ = fslots
    
    __options__ = options(
        size=numbers()
    )
    
    def __init__(self):
        self.multi = None
        
        if config["persist"]:
            self.cmd = "%s --persist" % config["exe"]
        else:
            self.cmd = config["exe"]
        
        self.xtics = Tics(name="x"), Tics(name="y"), Tics(name="z")
        # self.x, self.y, self.z = Axis("x"), Axis("y"), Axis("z")
        self.datafile = DataFile()
        self.global_sets, self.sets, self.commands, \
        self.ext, self.palette, self.count  = \
        {}, {}, [], None, None, 0
    
    
    def __del__(self):
        if self.multi is not None:
            self("unset multiplot")
    
    
    def __call__(self, *commands):
        self.commands.extend(commands)
        
        if config["debug"]:
            stderr.write("\n".join(commands))
    
    
    def __hash__(self):
        return phash((self.sets, tuple(self.commands)))
    
    def __setitem__(self, item, val):
        self.sets[item] = val
    
    def __getitem__(self, item):
        return self.sets[item]
    
    
    def line(self, pos, mode, start=0.0, stop=1.0, ref="graph", **kwargs):
        add = gp.parse_kwargs(**kwargs)
        
        if mode == "h" or mode == "horizontal":
            tpl = "from {ref} {}, {p} to {ref} {}, {p} nohead {}"
        elif mode == "v" or mode == "vertical":
            tpl = "from {p}, {ref} {} to {p}, {ref} {} nohead {}"
        else:
            raise ValueError('"mode" should be either "h", "horizontal", "v" '
                             'or "vertical"')

        self[arrow] = tpl.format(start, stop, " ".join(add), p=pos, ref=ref)
    
    def size(self, scale, square=False, ratio=None):
        Cmd = ""
        
        if square:
            Cmd += " square"
        else:
            Cmd += " no square"
        
        if ratio is not None:
            Cmd += " ratio %f" % (ratio)
        
        self[size] = "%s %f %f" % (Cmd, scale[0], scale[1])
    
    def margins(self, screen=False, **kwargs):
        fmt = "at screen %f" if screen else "%s"
        
        self.sets.update({key: fmt % value for key, value in kwargs.items()
                          if key in {"lmargin", "rmargin", 
                                     "tmargin", "bmargin"}})
        
    def path(self, data):
        return pth.join(tmp_path, "%s" % (phash(data.encode("ascii"))))
    
    
    def style(self, stylenum, ltype, **kwargs):
        self["style line %d" % stylenum] = \
        "%s" % (linedef(ltype, **kwargs))
    
    def refresh(self, plot_cmd, *items, **kwargs):
        assert plot_cmd in {"plot", "splot"}
        
        term(**kwargs)
        
        txt = "%s\n%s\n%s\n" % (
            "\n".join(parse_set(key, val)
                      for key, val in self.global_sets.items()),
            "\n".join(parse_set(key, val)
                      for key, val in self.sets.items()),
            "\n".join(self.commands)
        )
        
        
        if self.palette is not None:
            txt = "%s\n%s" % (txt, self.palette)
        
        txt = "%s\n%s %s\n" %  (txt,
                                plot_cmd,
                                ", ".join(plot.command for plot in items))
        
        path = "%s.%s" % (self.path(txt), self.ext)
        
        
        if not pth.isfile(path):
            txt = "set output '%s'\n%s" % (path, txt)
            
            # assert len({item.ptype for item in items}) == 1
            # ptype = items[0].ptype
            
            with open(gp_path, "w") as f:
                f.write(txt)
            
            try:
                sub.check_output(split("%s %s" % (self.cmd, gp_path)),
                                 stderr=sub.STDOUT)
            except sub.CalledProcessError as e:
                print(e.output.decode())
                raise e
        
        
        self.sets, self.commands, self.count = {}, [], 0
        
        return Plot(path)
        
    def plot_ipython(self, plot_cmd, *items, **kwargs):
        if Image is not None:
            kwargs.setdefault("term", "pngcairo")
            
            if not silent:
                path = self.refresh(plot_cmd, *items, **kwargs)
            
            display(Image(filename=str(path)))
            return path
        elif not silent:
            return refresh(plot_cmd, *items, **kwargs)
        
        
    def plot(self, *items, **kwargs):
        return self.plot_ipython("plot", *items, **kwargs)

    def splot(self, *items, **kwargs):
        return self.plot_ipython("splot", *items, **kwargs)


class Plot(namedtuple("Plot", "path")):
    def save(self, path):
        move(self.path, path)


@properties
class DataFile:
    prefix = "datafile"
    
    separator, binary, commentschars, missing, fortran = \
    None, None, None, None, None


@properties
class ColorBar(object):
    prefix = "colorbox"
    
    range, tics, format = None, None, None


class Axis(object):
    __slots__ = ("name", "_range", "_label", "options")
    
    def __init__(self, name="x"):
        self.name, self._range, self._label, self.options = \
        name, [], None, {}
        
    def __getitem__(self, k):
        if isinstance(k, slice):
            self.options["%stics" % self.name] = \
            "%f,%f,%f" % (k.start, k.step, k.stop)
    
    def set_range(self, _range):
        self._range = _range
        self.options["%srange" % self.name] = "[%f:%f]" % (_range[0], _range[1])
    
    def get_range(self):
        return self._range
    
    range = property(get_range, set_range)
    
    
    def set_label(self, label):
        self._label = label
        session["%slabel" % self.name] = "'%s'" % label

    
    def get_label(self):
        return self._label
    
    label = property(get_label, set_label)
    
    
    def get_format(self):
        return self._format
    
    def set_format(self, format):
        self._format = format
        session["format %s" % self.name] = "'%s'" % format
    
    format = property(get_format, set_format)
    

def data(*arrays, ltype="points", **kwargs):
    try:
        data = np.vstack(arrays).T
    except TypeError:
        raise DataError("Input arrays should be convertible to a "
                        "numpy array!")
    
    if data.ndim > 2:
        raise DataError("Only 1 or 2 dimensional arrays can be plotted!")
    
    text = convert_data(data, **kwargs)
    
    return PlotDescription("2D", text, **kwargs)


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
    
    text = convert_data(grid, grid=True, **kwargs)
    
    return PlotDescription("3D", text, **kwargs)

    
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
    
    text = "'%s'" % (data)

    if binary is not None and not isinstance(binary, bool):
        if array is not None:
            text += " binary array={} format='{}' "\
                    "endian={}".format(array, binary, endian)
        else:
            text += " binary format='{}' endian={}"\
                    .format(binary, endian)
    elif binary:
        text += " binary"
    
    return PlotDescription("2D", text, **kwargs)


def convert_data(data, grid=False, **kwargs):
    bytes = data.dumps()
    path = pth.join(data_path, "%s.dat" % phash(bytes))
    
    if not pth.isfile(path):
        data.tofile(path)
        # with open(path, "wb") as f:
        #     f.write(bytes)
    
    if grid:
        add = "binary matrix"
    else:
        add = arr_bin(data)
    
    return "'%s' %s" % (path, add)
    

def palette(pal):
    session.palette = color_palettes[pal]


def multiplot(nplot, **kwargs):
    raise NotImplemented("Multiplot functionality still in the works.")
#     return gp.MultiPlot(nplot, _session, **kwargs)


    

def unset_multi():
    call("unset multiplot")
    multi = None


def reset():
    call("reset")




# Convert this to property
def title(title):
    set(title=title)


def term(term, size=None, **kwargs):
    enhanced = bool(kwargs.pop("enhanced", False))
    
    
    session.ext = term2ext[term]
    
    if enhanced:
        term += " enhanced"
    
    if size is None:
        size = config["size"]
    
    term += " size %d,%d" % (size[0], size[1])
    
    
    if "font" in kwargs or "fontsize" in kwargs:
        term += font(**kwargs)
    
    set(terminal=term)


def font(font="Verdena", fontsize=12.0):
    return " font '%s, %d'" % (font, fontsize)


def output(outfile, **kwargs):
    if kwargs:
        term(**kwargs)
    
    set(output=outfile)


def arrow(From, to, style=None, tag=""):
    temp = "%s from %f,%f to %f,%f" % (tag, From[0], From[1], to[0], to[1])
    
    if style is not None:
        temp += " as %s" % (style)
    
    set(arrow=temp)


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
    def __init__(self, ptype, command, **kwargs):
        self.ptype, self.command = \
        ptype, command + parse_plot_arguments(**kwargs)
    
    def __str__(self):
        return self.command

    
    def __repr__(self):
        return "<PlotDescription ptype: %s, command: %s>" \
                % (self.ptype, self.command)


# *************************
# * Convenience functions *
# *************************


def arr_bin(array):
    if array.ndim == 1:
        return " binary format='%s'" % (len(array) * gp.fmt_dict[array.dtype])
    elif array.ndim == 2:
        fmt = array.shape[1] * fmt_dict[array.dtype]
        return " binary record=%d format='%s'" % (array.shape[0], fmt)


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
        return "lc %s '%s'" % (key, value)
    
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
    "rgbcolor",
    "commentschars",
    "output"
})


equaled = frozenset({
    "format",
    "filetype"
})


def parse_option(key, value):
    f = lambda x: x in key
    qtd, eqd = any(map(f, quoted)), any(map(f, equaled))
    
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


def parse_set(key, value, prefix=None):
    if prefix is None:
        tpl = "set %s"
    else:
        tpl = "set %s %%s" % prefix
    
    if value is True:
        return tpl % (key)
    elif value is False:
        return ("un" + tpl) % (key)
    else:
        return tpl % parse_option(key, value)


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
    "filled_rombus": 13
}


line_type_dict = {
    "black": -1,
    "dashed": 0,
    "red": 1,
    "green": 2,
    "blue": 3,
    "purple": 4,
    "teal": 5
}


term2ext = {
    "cgm": "cgm",
    "context": "tex",
    "corel": "eps",
    "dxf": "dxf",
    "eepic": "tex",
    "emf": "emf",
    "emtex": "tex",
    "epscairo": "eps",
    "epslatex": "tex",
    "fig": "fig",
    "gif": "gif",
    "gpic": "gpic",
    "jpeg": "jpeg",
    "latex": "tex",
    "mp": "mp",
    "pdfcairo": "pdf",
    "pngcairo": "png",
    "postscript": "ps",
    "pslatex": "tex",
    "pstex": "tex",
    "pstricks": "tex",
    "regis": "regis",
    "svg": "svg",
    "tikz": "tex"
}


dtype = np.dtype

fmt_dict = {
    dtype("float64"): "%float64",
    dtype("float32"): "%float",
    
    dtype("int8"): "%int8",
    dtype("int16"): "%int16",
    dtype("int32"): "%int32",
    dtype("int64"): "%int64",
    
    dtype("uint8"): "%uint8",
    dtype("uint16"): "%uint16",
    dtype("uint32"): "%uint32",
    dtype("uint64"): "%uint64"
}


# New matplotlib colormaps by Nathaniel J. Smith, Stefan van der Walt,
# and (in the case of viridis) Eric Firing.
#
# This file and the colormaps in it are released under the CC0 license /
# public domain dedication. We would appreciate credit if you use or
# redistribute these colormaps, but do not impose any legal restrictions.
#
# To the extent possible under law, the persons who associated CC0 with
# mpl-colormaps have waived all copyright and related or neighboring rights
# to mpl-colormaps.
#
# You should have received a copy of the CC0 legalcode along with this
# work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

# Colorpalettes taken from: https://github.com/BIDS/colormap/blob/master/colormaps.py


color_palettes = {

#********
# * JET *
#********

"jet":\
"""
# line styles
set style line 1 lt 1 lc rgb '#000080' #
set style line 2 lt 1 lc rgb '#0000ff' #
set style line 3 lt 1 lc rgb '#0080ff' #
set style line 4 lt 1 lc rgb '#00ffff' #
set style line 5 lt 1 lc rgb '#80ff80' #
set style line 6 lt 1 lc rgb '#ffff00' #
set style line 7 lt 1 lc rgb '#ff8000' #
set style line 8 lt 1 lc rgb '#ff0000' #
set style line 9 lt 1 lc rgb '#800000' #
# line style used together with jet (<2014b)
set style line 11 lt 1 lc rgb '#0000ff' # blue
set style line 12 lt 1 lc rgb '#007f00' # green
set style line 13 lt 1 lc rgb '#ff0000' # red
set style line 14 lt 1 lc rgb '#00bfbf' # cyan
set style line 15 lt 1 lc rgb '#bf00bf' # pink
set style line 16 lt 1 lc rgb '#bfbf00' # yellow
set style line 17 lt 1 lc rgb '#3f3f3f' # black
# palette
set palette defined (0  0.0 0.0 0.5, \
                     1  0.0 0.0 1.0, \
                     2  0.0 0.5 1.0, \
                     3  0.0 1.0 1.0, \
                     4  0.5 1.0 0.5, \
                     5  1.0 1.0 0.0, \
                     6  1.0 0.5 0.0, \
                     7  1.0 0.0 0.0, \
                     8  0.5 0.0 0.0 )

""",

#***********
# * PARULA *
#***********

"parula":\
"""
# line styles
set style line  1 lt 1 lc rgb '#352a87' # blue
set style line  2 lt 1 lc rgb '#0f5cdd' # blue
set style line  3 lt 1 lc rgb '#1481d6' # blue
set style line  4 lt 1 lc rgb '#06a4ca' # cyan
set style line  5 lt 1 lc rgb '#2eb7a4' # green
set style line  6 lt 1 lc rgb '#87bf77' # green
set style line  7 lt 1 lc rgb '#d1bb59' # orange
set style line  8 lt 1 lc rgb '#fec832' # orange
set style line  9 lt 1 lc rgb '#f9fb0e' # yellow

# New default Matlab line colors, introduced together with parula (2014b)
set style line 11 lt 1 lc rgb '#0072bd' # blue
set style line 12 lt 1 lc rgb '#d95319' # orange
set style line 13 lt 1 lc rgb '#edb120' # yellow
set style line 14 lt 1 lc rgb '#7e2f8e' # purple
set style line 15 lt 1 lc rgb '#77ac30' # green
set style line 16 lt 1 lc rgb '#4dbeee' # light-blue
set style line 17 lt 1 lc rgb '#a2142f' # red
# palette
set palette defined (\
0 '#352a87',\
1 '#0363e1',\
2 '#1485d4',\
3 '#06a7c6',\
4 '#38b99e',\
5 '#92bf73',\
6 '#d9ba56',\
7 '#fcce2e',\
8 '#f9fb0e')
""",

#***********
# * PLASMA *
#***********

"plasma":\
"""
# line styles
set style line  1 lt 1 lc rgb '#0c0887' # blue
set style line  2 lt 1 lc rgb '#4b03a1' # purple-blue
set style line  3 lt 1 lc rgb '#7d03a8' # purple
set style line  4 lt 1 lc rgb '#a82296' # purple
set style line  5 lt 1 lc rgb '#cb4679' # magenta
set style line  6 lt 1 lc rgb '#e56b5d' # red
set style line  7 lt 1 lc rgb '#f89441' # orange
set style line  8 lt 1 lc rgb '#fdc328' # orange
set style line  9 lt 1 lc rgb '#f0f921' # yellow
# palette
set palette defined (\
0   0.050383 0.029803 0.527975,\
1   0.063536 0.028426 0.533124,\
2   0.075353 0.027206 0.538007,\
3   0.086222 0.026125 0.542658,\
4   0.096379 0.025165 0.547103,\
5   0.105980 0.024309 0.551368,\
6   0.115124 0.023556 0.555468,\
7   0.123903 0.022878 0.559423,\
8   0.132381 0.022258 0.563250,\
9   0.140603 0.021687 0.566959,\
10  0.148607 0.021154 0.570562,\
11  0.156421 0.020651 0.574065,\
12  0.164070 0.020171 0.577478,\
13  0.171574 0.019706 0.580806,\
14  0.178950 0.019252 0.584054,\
15  0.186213 0.018803 0.587228,\
16  0.193374 0.018354 0.590330,\
17  0.200445 0.017902 0.593364,\
18  0.207435 0.017442 0.596333,\
19  0.214350 0.016973 0.599239,\
20  0.221197 0.016497 0.602083,\
21  0.227983 0.016007 0.604867,\
22  0.234715 0.015502 0.607592,\
23  0.241396 0.014979 0.610259,\
24  0.248032 0.014439 0.612868,\
25  0.254627 0.013882 0.615419,\
26  0.261183 0.013308 0.617911,\
27  0.267703 0.012716 0.620346,\
28  0.274191 0.012109 0.622722,\
29  0.280648 0.011488 0.625038,\
30  0.287076 0.010855 0.627295,\
31  0.293478 0.010213 0.629490,\
32  0.299855 0.009561 0.631624,\
33  0.306210 0.008902 0.633694,\
34  0.312543 0.008239 0.635700,\
35  0.318856 0.007576 0.637640,\
36  0.325150 0.006915 0.639512,\
37  0.331426 0.006261 0.641316,\
38  0.337683 0.005618 0.643049,\
39  0.343925 0.004991 0.644710,\
40  0.350150 0.004382 0.646298,\
41  0.356359 0.003798 0.647810,\
42  0.362553 0.003243 0.649245,\
43  0.368733 0.002724 0.650601,\
44  0.374897 0.002245 0.651876,\
45  0.381047 0.001814 0.653068,\
46  0.387183 0.001434 0.654177,\
47  0.393304 0.001114 0.655199,\
48  0.399411 0.000859 0.656133,\
49  0.405503 0.000678 0.656977,\
50  0.411580 0.000577 0.657730,\
51  0.417642 0.000564 0.658390,\
52  0.423689 0.000646 0.658956,\
53  0.429719 0.000831 0.659425,\
54  0.435734 0.001127 0.659797,\
55  0.441732 0.001540 0.660069,\
56  0.447714 0.002080 0.660240,\
57  0.453677 0.002755 0.660310,\
58  0.459623 0.003574 0.660277,\
59  0.465550 0.004545 0.660139,\
60  0.471457 0.005678 0.659897,\
61  0.477344 0.006980 0.659549,\
62  0.483210 0.008460 0.659095,\
63  0.489055 0.010127 0.658534,\
64  0.494877 0.011990 0.657865,\
65  0.500678 0.014055 0.657088,\
66  0.506454 0.016333 0.656202,\
67  0.512206 0.018833 0.655209,\
68  0.517933 0.021563 0.654109,\
69  0.523633 0.024532 0.652901,\
70  0.529306 0.027747 0.651586,\
71  0.534952 0.031217 0.650165,\
72  0.540570 0.034950 0.648640,\
73  0.546157 0.038954 0.647010,\
74  0.551715 0.043136 0.645277,\
75  0.557243 0.047331 0.643443,\
76  0.562738 0.051545 0.641509,\
77  0.568201 0.055778 0.639477,\
78  0.573632 0.060028 0.637349,\
79  0.579029 0.064296 0.635126,\
80  0.584391 0.068579 0.632812,\
81  0.589719 0.072878 0.630408,\
82  0.595011 0.077190 0.627917,\
83  0.600266 0.081516 0.625342,\
84  0.605485 0.085854 0.622686,\
85  0.610667 0.090204 0.619951,\
86  0.615812 0.094564 0.617140,\
87  0.620919 0.098934 0.614257,\
88  0.625987 0.103312 0.611305,\
89  0.631017 0.107699 0.608287,\
90  0.636008 0.112092 0.605205,\
91  0.640959 0.116492 0.602065,\
92  0.645872 0.120898 0.598867,\
93  0.650746 0.125309 0.595617,\
94  0.655580 0.129725 0.592317,\
95  0.660374 0.134144 0.588971,\
96  0.665129 0.138566 0.585582,\
97  0.669845 0.142992 0.582154,\
98  0.674522 0.147419 0.578688,\
99  0.679160 0.151848 0.575189,\
100 0.683758 0.156278 0.571660,\
101 0.688318 0.160709 0.568103,\
102 0.692840 0.165141 0.564522,\
103 0.697324 0.169573 0.560919,\
104 0.701769 0.174005 0.557296,\
105 0.706178 0.178437 0.553657,\
106 0.710549 0.182868 0.550004,\
107 0.714883 0.187299 0.546338,\
108 0.719181 0.191729 0.542663,\
109 0.723444 0.196158 0.538981,\
110 0.727670 0.200586 0.535293,\
111 0.731862 0.205013 0.531601,\
112 0.736019 0.209439 0.527908,\
113 0.740143 0.213864 0.524216,\
114 0.744232 0.218288 0.520524,\
115 0.748289 0.222711 0.516834,\
116 0.752312 0.227133 0.513149,\
117 0.756304 0.231555 0.509468,\
118 0.760264 0.235976 0.505794,\
119 0.764193 0.240396 0.502126,\
120 0.768090 0.244817 0.498465,\
121 0.771958 0.249237 0.494813,\
122 0.775796 0.253658 0.491171,\
123 0.779604 0.258078 0.487539,\
124 0.783383 0.262500 0.483918,\
125 0.787133 0.266922 0.480307,\
126 0.790855 0.271345 0.476706,\
127 0.794549 0.275770 0.473117,\
128 0.798216 0.280197 0.469538,\
129 0.801855 0.284626 0.465971,\
130 0.805467 0.289057 0.462415,\
131 0.809052 0.293491 0.458870,\
132 0.812612 0.297928 0.455338,\
133 0.816144 0.302368 0.451816,\
134 0.819651 0.306812 0.448306,\
135 0.823132 0.311261 0.444806,\
136 0.826588 0.315714 0.441316,\
137 0.830018 0.320172 0.437836,\
138 0.833422 0.324635 0.434366,\
139 0.836801 0.329105 0.430905,\
140 0.840155 0.333580 0.427455,\
141 0.843484 0.338062 0.424013,\
142 0.846788 0.342551 0.420579,\
143 0.850066 0.347048 0.417153,\
144 0.853319 0.351553 0.413734,\
145 0.856547 0.356066 0.410322,\
146 0.859750 0.360588 0.406917,\
147 0.862927 0.365119 0.403519,\
148 0.866078 0.369660 0.400126,\
149 0.869203 0.374212 0.396738,\
150 0.872303 0.378774 0.393355,\
151 0.875376 0.383347 0.389976,\
152 0.878423 0.387932 0.386600,\
153 0.881443 0.392529 0.383229,\
154 0.884436 0.397139 0.379860,\
155 0.887402 0.401762 0.376494,\
156 0.890340 0.406398 0.373130,\
157 0.893250 0.411048 0.369768,\
158 0.896131 0.415712 0.366407,\
159 0.898984 0.420392 0.363047,\
160 0.901807 0.425087 0.359688,\
161 0.904601 0.429797 0.356329,\
162 0.907365 0.434524 0.352970,\
163 0.910098 0.439268 0.349610,\
164 0.912800 0.444029 0.346251,\
165 0.915471 0.448807 0.342890,\
166 0.918109 0.453603 0.339529,\
167 0.920714 0.458417 0.336166,\
168 0.923287 0.463251 0.332801,\
169 0.925825 0.468103 0.329435,\
170 0.928329 0.472975 0.326067,\
171 0.930798 0.477867 0.322697,\
172 0.933232 0.482780 0.319325,\
173 0.935630 0.487712 0.315952,\
174 0.937990 0.492667 0.312575,\
175 0.940313 0.497642 0.309197,\
176 0.942598 0.502639 0.305816,\
177 0.944844 0.507658 0.302433,\
178 0.947051 0.512699 0.299049,\
179 0.949217 0.517763 0.295662,\
180 0.951344 0.522850 0.292275,\
181 0.953428 0.527960 0.288883,\
182 0.955470 0.533093 0.285490,\
183 0.957469 0.538250 0.282096,\
184 0.959424 0.543431 0.278701,\
185 0.961336 0.548636 0.275305,\
186 0.963203 0.553865 0.271909,\
187 0.965024 0.559118 0.268513,\
188 0.966798 0.564396 0.265118,\
189 0.968526 0.569700 0.261721,\
190 0.970205 0.575028 0.258325,\
191 0.971835 0.580382 0.254931,\
192 0.973416 0.585761 0.251540,\
193 0.974947 0.591165 0.248151,\
194 0.976428 0.596595 0.244767,\
195 0.977856 0.602051 0.241387,\
196 0.979233 0.607532 0.238013,\
197 0.980556 0.613039 0.234646,\
198 0.981826 0.618572 0.231287,\
199 0.983041 0.624131 0.227937,\
200 0.984199 0.629718 0.224595,\
201 0.985301 0.635330 0.221265,\
202 0.986345 0.640969 0.217948,\
203 0.987332 0.646633 0.214648,\
204 0.988260 0.652325 0.211364,\
205 0.989128 0.658043 0.208100,\
206 0.989935 0.663787 0.204859,\
207 0.990681 0.669558 0.201642,\
208 0.991365 0.675355 0.198453,\
209 0.991985 0.681179 0.195295,\
210 0.992541 0.687030 0.192170,\
211 0.993032 0.692907 0.189084,\
212 0.993456 0.698810 0.186041,\
213 0.993814 0.704741 0.183043,\
214 0.994103 0.710698 0.180097,\
215 0.994324 0.716681 0.177208,\
216 0.994474 0.722691 0.174381,\
217 0.994553 0.728728 0.171622,\
218 0.994561 0.734791 0.168938,\
219 0.994495 0.740880 0.166335,\
220 0.994355 0.746995 0.163821,\
221 0.994141 0.753137 0.161404,\
222 0.993851 0.759304 0.159092,\
223 0.993482 0.765499 0.156891,\
224 0.993033 0.771720 0.154808,\
225 0.992505 0.777967 0.152855,\
226 0.991897 0.784239 0.151042,\
227 0.991209 0.790537 0.149377,\
228 0.990439 0.796859 0.147870,\
229 0.989587 0.803205 0.146529,\
230 0.988648 0.809579 0.145357,\
231 0.987621 0.815978 0.144363,\
232 0.986509 0.822401 0.143557,\
233 0.985314 0.828846 0.142945,\
234 0.984031 0.835315 0.142528,\
235 0.982653 0.841812 0.142303,\
236 0.981190 0.848329 0.142279,\
237 0.979644 0.854866 0.142453,\
238 0.977995 0.861432 0.142808,\
239 0.976265 0.868016 0.143351,\
240 0.974443 0.874622 0.144061,\
241 0.972530 0.881250 0.144923,\
242 0.970533 0.887896 0.145919,\
243 0.968443 0.894564 0.147014,\
244 0.966271 0.901249 0.148180,\
245 0.964021 0.907950 0.149370,\
246 0.961681 0.914672 0.150520,\
247 0.959276 0.921407 0.151566,\
248 0.956808 0.928152 0.152409,\
249 0.954287 0.934908 0.152921,\
250 0.951726 0.941671 0.152925,\
251 0.949151 0.948435 0.152178,\
252 0.946602 0.955190 0.150328,\
253 0.944152 0.961916 0.146861,\
254 0.941896 0.968590 0.140956,\
255 0.940015 0.975158 0.131326)
""",

#************
# * VIRIDIS *
#************

"viridis":\
"""
# line styles
set style line  1 lt 1 lc rgb '#440154' # dark purple
set style line  2 lt 1 lc rgb '#472c7a' # purple
set style line  3 lt 1 lc rgb '#3b518b' # blue
set style line  4 lt 1 lc rgb '#2c718e' # blue
set style line  5 lt 1 lc rgb '#21908d' # blue-green
set style line  6 lt 1 lc rgb '#27ad81' # green
set style line  7 lt 1 lc rgb '#5cc863' # green
set style line  8 lt 1 lc rgb '#aadc32' # lime green
set style line  9 lt 1 lc rgb '#fde725' # yellow
# palette
set palette defined (\
0   0.267004 0.004874 0.329415,\
1   0.268510 0.009605 0.335427,\
2   0.269944 0.014625 0.341379,\
3   0.271305 0.019942 0.347269,\
4   0.272594 0.025563 0.353093,\
5   0.273809 0.031497 0.358853,\
6   0.274952 0.037752 0.364543,\
7   0.276022 0.044167 0.370164,\
8   0.277018 0.050344 0.375715,\
9   0.277941 0.056324 0.381191,\
10  0.278791 0.062145 0.386592,\
11  0.279566 0.067836 0.391917,\
12  0.280267 0.073417 0.397163,\
13  0.280894 0.078907 0.402329,\
14  0.281446 0.084320 0.407414,\
15  0.281924 0.089666 0.412415,\
16  0.282327 0.094955 0.417331,\
17  0.282656 0.100196 0.422160,\
18  0.282910 0.105393 0.426902,\
19  0.283091 0.110553 0.431554,\
20  0.283197 0.115680 0.436115,\
21  0.283229 0.120777 0.440584,\
22  0.283187 0.125848 0.444960,\
23  0.283072 0.130895 0.449241,\
24  0.282884 0.135920 0.453427,\
25  0.282623 0.140926 0.457517,\
26  0.282290 0.145912 0.461510,\
27  0.281887 0.150881 0.465405,\
28  0.281412 0.155834 0.469201,\
29  0.280868 0.160771 0.472899,\
30  0.280255 0.165693 0.476498,\
31  0.279574 0.170599 0.479997,\
32  0.278826 0.175490 0.483397,\
33  0.278012 0.180367 0.486697,\
34  0.277134 0.185228 0.489898,\
35  0.276194 0.190074 0.493001,\
36  0.275191 0.194905 0.496005,\
37  0.274128 0.199721 0.498911,\
38  0.273006 0.204520 0.501721,\
39  0.271828 0.209303 0.504434,\
40  0.270595 0.214069 0.507052,\
41  0.269308 0.218818 0.509577,\
42  0.267968 0.223549 0.512008,\
43  0.266580 0.228262 0.514349,\
44  0.265145 0.232956 0.516599,\
45  0.263663 0.237631 0.518762,\
46  0.262138 0.242286 0.520837,\
47  0.260571 0.246922 0.522828,\
48  0.258965 0.251537 0.524736,\
49  0.257322 0.256130 0.526563,\
50  0.255645 0.260703 0.528312,\
51  0.253935 0.265254 0.529983,\
52  0.252194 0.269783 0.531579,\
53  0.250425 0.274290 0.533103,\
54  0.248629 0.278775 0.534556,\
55  0.246811 0.283237 0.535941,\
56  0.244972 0.287675 0.537260,\
57  0.243113 0.292092 0.538516,\
58  0.241237 0.296485 0.539709,\
59  0.239346 0.300855 0.540844,\
60  0.237441 0.305202 0.541921,\
61  0.235526 0.309527 0.542944,\
62  0.233603 0.313828 0.543914,\
63  0.231674 0.318106 0.544834,\
64  0.229739 0.322361 0.545706,\
65  0.227802 0.326594 0.546532,\
66  0.225863 0.330805 0.547314,\
67  0.223925 0.334994 0.548053,\
68  0.221989 0.339161 0.548752,\
69  0.220057 0.343307 0.549413,\
70  0.218130 0.347432 0.550038,\
71  0.216210 0.351535 0.550627,\
72  0.214298 0.355619 0.551184,\
73  0.212395 0.359683 0.551710,\
74  0.210503 0.363727 0.552206,\
75  0.208623 0.367752 0.552675,\
76  0.206756 0.371758 0.553117,\
77  0.204903 0.375746 0.553533,\
78  0.203063 0.379716 0.553925,\
79  0.201239 0.383670 0.554294,\
80  0.199430 0.387607 0.554642,\
81  0.197636 0.391528 0.554969,\
82  0.195860 0.395433 0.555276,\
83  0.194100 0.399323 0.555565,\
84  0.192357 0.403199 0.555836,\
85  0.190631 0.407061 0.556089,\
86  0.188923 0.410910 0.556326,\
87  0.187231 0.414746 0.556547,\
88  0.185556 0.418570 0.556753,\
89  0.183898 0.422383 0.556944,\
90  0.182256 0.426184 0.557120,\
91  0.180629 0.429975 0.557282,\
92  0.179019 0.433756 0.557430,\
93  0.177423 0.437527 0.557565,\
94  0.175841 0.441290 0.557685,\
95  0.174274 0.445044 0.557792,\
96  0.172719 0.448791 0.557885,\
97  0.171176 0.452530 0.557965,\
98  0.169646 0.456262 0.558030,\
99  0.168126 0.459988 0.558082,\
100 0.166617 0.463708 0.558119,\
101 0.165117 0.467423 0.558141,\
102 0.163625 0.471133 0.558148,\
103 0.162142 0.474838 0.558140,\
104 0.160665 0.478540 0.558115,\
105 0.159194 0.482237 0.558073,\
106 0.157729 0.485932 0.558013,\
107 0.156270 0.489624 0.557936,\
108 0.154815 0.493313 0.557840,\
109 0.153364 0.497000 0.557724,\
110 0.151918 0.500685 0.557587,\
111 0.150476 0.504369 0.557430,\
112 0.149039 0.508051 0.557250,\
113 0.147607 0.511733 0.557049,\
114 0.146180 0.515413 0.556823,\
115 0.144759 0.519093 0.556572,\
116 0.143343 0.522773 0.556295,\
117 0.141935 0.526453 0.555991,\
118 0.140536 0.530132 0.555659,\
119 0.139147 0.533812 0.555298,\
120 0.137770 0.537492 0.554906,\
121 0.136408 0.541173 0.554483,\
122 0.135066 0.544853 0.554029,\
123 0.133743 0.548535 0.553541,\
124 0.132444 0.552216 0.553018,\
125 0.131172 0.555899 0.552459,\
126 0.129933 0.559582 0.551864,\
127 0.128729 0.563265 0.551229,\
128 0.127568 0.566949 0.550556,\
129 0.126453 0.570633 0.549841,\
130 0.125394 0.574318 0.549086,\
131 0.124395 0.578002 0.548287,\
132 0.123463 0.581687 0.547445,\
133 0.122606 0.585371 0.546557,\
134 0.121831 0.589055 0.545623,\
135 0.121148 0.592739 0.544641,\
136 0.120565 0.596422 0.543611,\
137 0.120092 0.600104 0.542530,\
138 0.119738 0.603785 0.541400,\
139 0.119512 0.607464 0.540218,\
140 0.119423 0.611141 0.538982,\
141 0.119483 0.614817 0.537692,\
142 0.119699 0.618490 0.536347,\
143 0.120081 0.622161 0.534946,\
144 0.120638 0.625828 0.533488,\
145 0.121380 0.629492 0.531973,\
146 0.122312 0.633153 0.530398,\
147 0.123444 0.636809 0.528763,\
148 0.124780 0.640461 0.527068,\
149 0.126326 0.644107 0.525311,\
150 0.128087 0.647749 0.523491,\
151 0.130067 0.651384 0.521608,\
152 0.132268 0.655014 0.519661,\
153 0.134692 0.658636 0.517649,\
154 0.137339 0.662252 0.515571,\
155 0.140210 0.665859 0.513427,\
156 0.143303 0.669459 0.511215,\
157 0.146616 0.673050 0.508936,\
158 0.150148 0.676631 0.506589,\
159 0.153894 0.680203 0.504172,\
160 0.157851 0.683765 0.501686,\
161 0.162016 0.687316 0.499129,\
162 0.166383 0.690856 0.496502,\
163 0.170948 0.694384 0.493803,\
164 0.175707 0.697900 0.491033,\
165 0.180653 0.701402 0.488189,\
166 0.185783 0.704891 0.485273,\
167 0.191090 0.708366 0.482284,\
168 0.196571 0.711827 0.479221,\
169 0.202219 0.715272 0.476084,\
170 0.208030 0.718701 0.472873,\
171 0.214000 0.722114 0.469588,\
172 0.220124 0.725509 0.466226,\
173 0.226397 0.728888 0.462789,\
174 0.232815 0.732247 0.459277,\
175 0.239374 0.735588 0.455688,\
176 0.246070 0.738910 0.452024,\
177 0.252899 0.742211 0.448284,\
178 0.259857 0.745492 0.444467,\
179 0.266941 0.748751 0.440573,\
180 0.274149 0.751988 0.436601,\
181 0.281477 0.755203 0.432552,\
182 0.288921 0.758394 0.428426,\
183 0.296479 0.761561 0.424223,\
184 0.304148 0.764704 0.419943,\
185 0.311925 0.767822 0.415586,\
186 0.319809 0.770914 0.411152,\
187 0.327796 0.773980 0.406640,\
188 0.335885 0.777018 0.402049,\
189 0.344074 0.780029 0.397381,\
190 0.352360 0.783011 0.392636,\
191 0.360741 0.785964 0.387814,\
192 0.369214 0.788888 0.382914,\
193 0.377779 0.791781 0.377939,\
194 0.386433 0.794644 0.372886,\
195 0.395174 0.797475 0.367757,\
196 0.404001 0.800275 0.362552,\
197 0.412913 0.803041 0.357269,\
198 0.421908 0.805774 0.351910,\
199 0.430983 0.808473 0.346476,\
200 0.440137 0.811138 0.340967,\
201 0.449368 0.813768 0.335384,\
202 0.458674 0.816363 0.329727,\
203 0.468053 0.818921 0.323998,\
204 0.477504 0.821444 0.318195,\
205 0.487026 0.823929 0.312321,\
206 0.496615 0.826376 0.306377,\
207 0.506271 0.828786 0.300362,\
208 0.515992 0.831158 0.294279,\
209 0.525776 0.833491 0.288127,\
210 0.535621 0.835785 0.281908,\
211 0.545524 0.838039 0.275626,\
212 0.555484 0.840254 0.269281,\
213 0.565498 0.842430 0.262877,\
214 0.575563 0.844566 0.256415,\
215 0.585678 0.846661 0.249897,\
216 0.595839 0.848717 0.243329,\
217 0.606045 0.850733 0.236712,\
218 0.616293 0.852709 0.230052,\
219 0.626579 0.854645 0.223353,\
220 0.636902 0.856542 0.216620,\
221 0.647257 0.858400 0.209861,\
222 0.657642 0.860219 0.203082,\
223 0.668054 0.861999 0.196293,\
224 0.678489 0.863742 0.189503,\
225 0.688944 0.865448 0.182725,\
226 0.699415 0.867117 0.175971,\
227 0.709898 0.868751 0.169257,\
228 0.720391 0.870350 0.162603,\
229 0.730889 0.871916 0.156029,\
230 0.741388 0.873449 0.149561,\
231 0.751884 0.874951 0.143228,\
232 0.762373 0.876424 0.137064,\
233 0.772852 0.877868 0.131109,\
234 0.783315 0.879285 0.125405,\
235 0.793760 0.880678 0.120005,\
236 0.804182 0.882046 0.114965,\
237 0.814576 0.883393 0.110347,\
238 0.824940 0.884720 0.106217,\
239 0.835270 0.886029 0.102646,\
240 0.845561 0.887322 0.099702,\
241 0.855810 0.888601 0.097452,\
242 0.866013 0.889868 0.095953,\
243 0.876168 0.891125 0.095250,\
244 0.886271 0.892374 0.095374,\
245 0.896320 0.893616 0.096335,\
246 0.906311 0.894855 0.098125,\
247 0.916242 0.896091 0.100717,\
248 0.926106 0.897330 0.104071,\
249 0.935904 0.898570 0.108131,\
250 0.945636 0.899815 0.112838,\
251 0.955300 0.901065 0.118128,\
252 0.964894 0.902323 0.123941,\
253 0.974417 0.903590 0.130215,\
254 0.983868 0.904867 0.136897,\
255 0.993248 0.906157 0.143936)
""",

#***********
# * YLGNBU *
#***********
# line styles for ColorBrewer YlGnBu
# for use with sequential data
# provides 8 yellow-green-blue colors of increasing saturation
# compatible with gnuplot >=4.2
# author: Anna Schneider

"ylgnbu":\
"""
# line styles
set style line 1 lt 1 lc rgb '#FFFFD9' # very light yellow-green-blue
set style line 2 lt 1 lc rgb '#EDF8B1' # 
set style line 3 lt 1 lc rgb '#C7E9B4' # 
set style line 4 lt 1 lc rgb '#7FCDBB' # light yellow-green-blue
set style line 5 lt 1 lc rgb '#41B6C4' # 
set style line 6 lt 1 lc rgb '#1D91C0' # medium yellow-green-blue
set style line 7 lt 1 lc rgb '#225EA8' #
set style line 8 lt 1 lc rgb '#0C2C84' # dark yellow-green-blue
# palette
set palette defined ( 0 '#FFFFD9',\
                      1 '#EDF8B1',\
                      2 '#C7E9B4',\
                      3 '#7FCDBB',\
                      4 '#41B6C4',\
                      5 '#1D91C0',\
                      6 '#225EA8',\
                      7 '#0C2C84' )
"""
}
