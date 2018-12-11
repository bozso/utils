from math import ceil, sqrt
from re import sub
import gmt.private as gp

_gmt = gp.GMT()

_current_module = __import__(__name__)


for cmd in gp.gmt_commands:
    setattr(_current_module, cmd, gp.make_cmd(cmd))

    
def out(outfile):
    _gmt.out = outfile

def common(**kwargs):
    _gmt.common = " ".join(("-{}{}".format(key, proc_flag(flag))
                            for key, flag in kwargs.items()))


def output(outfile, **kwargs):
    _gmt.out = outfile
    common(**kwargs)


def config(**kwargs):
    # convert keys to uppercase
    config = {key.upper(): value for key, value in config.items()}
    _gmt.config.update(config)
    

def debug(default=True):
    _gmt.debug = default


def raster(out, **kwargs):
    dpi           = float(kwargs.pop("dpi", 200))
    gray          = bool(kwargs.pop("gray", False))
    portrait      = bool(kwargs.pop("portrait", False))
    with_pagesize = bool(kwargs.pop("with_pagesize", False))
    multi_page    = bool(kwargs.pop("multi_page", False))
    transparent   = bool(kwargs.pop("transparent", False))
    
    name, ext = pth.splitext(out)
    
    if self.is_five:
        Cmd = "gmt ps2raster"
    else:
        Cmd = "ps2raster"
    
    # extension code
    Ext = gp.ps2raster[ext]
    
    # handle extra options
    
    if with_pagesize:
        if ext == ".eps":
            Ext = Ext.upper()
        else:
            raise ValueError("with_pagesize only available for EPS files.")
        
    if multi_page:
        if ext == ".pdf":
            Ext = Ext.upper()
        else:
            raise ValueError("multi_page only available for PDF files.")
    
    if transparent:
        if ext == ".png":
            Ext = Ext.upper()
        else:
            raise ValueError("transparent only available for PNG files.")

    
    Cmd = "{} {} -T{} -E{} -F{}"\
          .format(Cmd, _gmt.out, Ext, dpi, name)
    
    if gray:
        Cmd += " -I"
    
    if portrait:
        Cmd += " -P"
    
    cmd(Cmd)


def reform(**common_flags):
    # if we have common flags parse them
    if len(common_flags) > 0:
        _gmt.common = " ".join(["-{}{}".format(key, proc_flag(flag))
                                for key, flag in common_flags.items()])
    else:
        _gmt.common = None

    
def makecpt(outfile, **flags):
    keys = flags.keys()
    
    if len(keys) > 0:
        gmt_flags = ("-{}{}".format(key, proc_flag(flags[key]))
                     for key in keys)
    
    _gmt.commands.append(("makecpt", " ".join(gmt_flags), None, outfile))


def set(parameter, value):
    _gmt.commands.append(("set {}={}".format(parameter, value),
                          None, None, None))


def get_config(key):
    return _self.config[key.upper()]

def get_width():
    
    if self.is_gmt5:
        Cmd = "gmt mapproject {} -Dp".format(_gmt.common)
        version = get_version()
    else:
        Cmd = "mapproject {} -Dp".format(_gmt.common)
    
    if not _gmt.version >= _gmt_five_two:
        # before version 5.2
        Cmd += " {} -V".format(os.devnull)
        out = [line for line in cmd(Cmd, ret=True).split("\n")
               if "Transform" in line]
        return float(out[0].split("/")[4])
    else:
        Cmd += " -Ww"
        return float(cmd(Cmd, ret=True))


def get_height():
    
    if _gmt.is_gmt5:
        Cmd = "gmt mapproject {} -Dp".format(_gmt.common)
        version = get_version()
    else:
        Cmd = "mapproject {} -Dp".format(_gmt.common)
    
    if not _gmt.version >= _gmt_five_two:
        # before version 5.2
        Cmd += " {} -V".format(os.devnull)
        out = [line for line in cmd(Cmd, ret=True).split("\n")
               if "Transform" in line]
        return float(out[0].split("/")[6].split()[0])
    else:
        Cmd += " -Wh"
        return float(cmd(Cmd, ret=True))

    
def get_common_flag(flag):
    return _gmt.common.split(flag)[1].split()[0]


def multiplot(nplots, proj, nrows=None, **kwargs):
    """
         |       top           |    
    -----+---------------------+----
      l  |                     |  r
      e  |                     |  i
      f  |                     |  g
      t  |                     |  h
         |                     |  t
    -----+---------------------+----
         |       bottom        |    
    """
    xpad  = float(kwargs.pop("hpad", 55))
    ypad  = float(kwargs.pop("hpad", 75))
    top   = float(kwargs.pop("top", 0))
    left  = float(kwargs.pop("left", 0))
    right = float(kwargs.pop("right", 0))
    
    if nrows is None:
        nrows = ceil(sqrt(nplots) - 1)
        nrows = max([1, nrows])
    
    _gmt.left, _gmt.right, _gmt.top  = left, top, right
    
    ncols = ceil(nplots / nrows)
    
    width, height = _gmt.width, _gmt.height
    
    # width available for plotting
    awidth = width - (left + right)
    
    # width of a single plot
    pwidth  = float(awidth - (ncols - 1) * xpad) / ncols
    
    _gmt.common += " -J{}{}p".format(proj, pwidth)
    
    # height of a single plot
    pheight = get_height()
    
    # calculate psbasemap shifts in x and y directions
    x = (left + ii * (pwidth + xpad) for jj in range(nrows)
                                     for ii in range(ncols))
    
    y = (height - top - ii * (pheight + ypad)
         for ii in range(1, nrows + 1)
         for jj in range(ncols))
    
    # residual margin left at the bottom
    _gmt.bottom = height - top - nrows * pheight
    
    return tuple(x), tuple(y)


def scale_pos(mode, offset=100, flong=0.8, fshort=0.2):
    left, right, top, bottom = _gmt.left, _gmt.right, _gmt.top, _gmt.bottom
    
    width, height = _gmt.width, _gmt.height
    
    if mode == "vertical" or mode == "v":
        x = width - left - offset
        y = float(height) / 2
        
        # fraction of space available
        width  = fshort * left
        length = flong * height
        hor = ""
    elif mode == "horizontal" or mode == "h":
        x = float(self.width) / 2
        y = bottom - offset
        
        # fraction of space available
        length  = flong * width
        width   = fshort * bottom
        hor = "h"
    else:
        raise ValueError('mode should be either: "vertical", "horizontal", '
                         '"v" or "h", not "{}"'.format(mode))
    
    return str(x) + "p", str(y) + "p", str(length) + "p",\
           str(width) + "p" +  hor


def colorbar(mode="v", offset=100, flong=0.8, fshort=0.2, **flags):
    
    xx, yy, length, width = scale_pos(mode, offset=offset, flong=flong,
                                      fshort=fshort)

    _gmt.psscale(D=(0.0, 0.0, length, width), Xf=xx, Yf=yy, **flags)

# end GMT


def get_paper_size(paper, is_portrait=False):
    """ Get paper width and height. """

    if paper.startswith("a") or paper.startswith("b"):
        paper = paper.upper()

    if is_portrait:
        width, height = _gmt_paper_sizes[paper]
    else:
        height, width = _gmt_paper_sizes[paper]
    
    return width, height

    
def proc_flag(flag):
    """ Parse GMT flags. """
    if isinstance(flag, bool) and flag:
        return ""
    elif hasattr(flag, "__iter__") and not isinstance(flag, string_types):
        return "/".join(str(elem) for elem in flag)
    elif flag is None:
        return ""
    else:
        return flag


dem_dtypes = {
    "r4":"f"
}


def get_par(parameter, search):
    search_type = type(search)
    
    if search_type == list:
        searchfile = search
    elif os.path.isfile(search):
        with open(search, "r") as f:
            searchfile = f.readlines()
    else:
        raise ValueError("search should be either a list or a string that "
                         "describes a path to the parameter file.")
    
    parameter_value = None
    
    for line in searchfile:
        if parameter in line and not line.startswith("//"):
            parameter_value = " ".join(line.split()[1:]).split("//")[0].strip()
            break

    return parameter_value
