import os
import os.path as pth
import subprocess as subp
from shlex import split
from distutils.version import StrictVersion
from argparse import ArgumentParser
# python 2/3 compatibility
from six import string_types

def cmd(Cmd):
    """
    Execute terminal command defined by `cmd`, optionally return the
    output of the executed command if `ret` is set to True.
    """
    try:
        cmd_out = subp.check_output(split(Cmd), stderr=subp.STDOUT)
    except subp.CalledProcessError as e:
        print("ERROR: Non zero returncode from command: '{}'".format(Cmd))
        print("OUTPUT OF THE COMMAND: \n{}".format(e.output.decode()))
        print("RETURNCODE was: {}".format(e.returncode))
        
        raise e
        
    return " ".join(elem for elem in cmd_out.decode().split("\n")
                    if not elem.startswith("gmt:"))


def gmt(module, *args, **kwargs):
    
    if module not in gp.gmt_commands and "gmt" + module not in gp.gmt_commands:
        raise ValueError("Unrecognized gmt module: {}".format(module))
    
    if not module.startswith("gmt") and get_version() > _gmt_five:
        module = "gmt " + module
    
    Cmd = module + " " + " ".join(str(arg) for arg in args)

    if len(kwargs) > 0:
        Cmd += " " + " ".join(("-{}{}".format(key, proc_flag(flag))
                               for key, flag in kwargs.items()))
    
    return cmd(Cmd)


def get_version():
    """ Get the version of the installed GMT as a Strict Version object. """
    return StrictVersion(cmd("gmt --version", ret=True).strip())

class GMT(object):
    def __init__(self):
        
        # no margins by default
        self.left, self.right, self.top, self.bottom = 0.0, 0.0, 0.0, 0.0
        
        self.out, self.common, self.finalized = None, None, False
        
        # get GMT version
        self.version = get_version()
        
        if self.version > _gmt_five:
            self.is_gmt5 = True
        else:
            self.is_gmt5 = False
        
        self.config = _gmt_defaults
        
            
        if self.config["PS_PAGE_ORIENTATION"] == "portrait":
            self.is_portrait = True
        elif self.config["PS_PAGE_ORIENTATION"] == "landscape":
            self.is_portrait = False
        else:
            raise ValueError('PS_PAGE_ORIENTATION should be either '
                             '"portrait" or "landscape"')
        
        # get paper width and height
        paper = self["ps_media"]

        if paper.startswith("a") or paper.startswith("b"):
            paper = paper.upper()

        if self.is_portrait:
            self.width, self.height = _gmt_paper_sizes[paper]
        else:
            self.height, self.width = _gmt_paper_sizes[paper]
            
        with open("gmt.conf", "w") as f:
            f.write(_gmt_defaults_header)
            f.write("\n".join("{} = {}".format(key.upper(), value)
                              for key, value in self.config.items()))
        
        # list of lists that contains the gmt commands, its arguments, input
        # data and the filename where the command outputs will be written
        self.commands = []
        self.debug = False
        


    def __getitem__(self, key):
        return self.config[key.upper()]
        
    
    def finalize(self):
        commands = self.commands
        
        # indices of plotter functions
        idx = tuple(ii for ii, Cmd in enumerate(commands) if Cmd[0] in _plotters)
        
        # add -K, -P and -O flags to plotter functions
        if len(idx) > 1:
            for ii in idx[:-1]:
                commands[ii][1] += " -K"

            for ii in idx[1:]:
                commands[ii][1] += " -O"
            
        if self.is_portrait:
            for ii in idx:
                commands[ii][1] += " -P"
        
        if self.is_gmt5:
            commands = (("gmt " + Cmd[0], Cmd[1], Cmd[2], Cmd[3])
                        for Cmd in commands)
        
        # print commands for debugging
        if self.debug:
            print("\n".join(" ".join(elem for elem in Cmd[0:2])
                                          for Cmd in commands))
        
        # gather all the outputfiles and remove the ones that already exist
        outfiles = set(Cmd[3] for Cmd in commands
                       if Cmd[3] is not None and pth.isfile(Cmd[3]))
        
        for out in outfiles:
            os.remove(out)
        
        # execute gmt commands and write their output to the specified files
        for Cmd in commands:
            _execute_gmt_cmd(Cmd)
        
        # Cleanup
        if pth.isfile("gmt.history"):
            os.remove("gmt.history")
        os.remove("gmt.conf")
        
        self.finalized = True
    
    def __del__(self):
        if not self.finalized:
            self.finalize()


def _execute_gmt_cmd(Cmd, ret_out=False):
    # join command and flags
    cmd_out = cmd("{} {}".format(Cmd[0], Cmd[1]))
        
    if Cmd[3] is not None:
        with open(Cmd[3], "a") as f:
            f.write(cmd_out)
    

def make_cmd(gmt_exec):
    def f(data=None, byte_swap=False, outfile=None, **flags):
        if data is not None:
            if isinstance(data, string_types) and pth.isfile(data):
            # data is a path to a file
                gmt_flags = "{} ".format(data)
                data = None
            elif isinstance(data, list) or isinstance(data, tuple):
                data = ("\n".join(elem for elem in data)).encode()
                gmt_flags = ""
            else:
                raise ValueError("`data` should be a path to an existing file!")
        else:
            gmt_flags = ""
        
        # if we have flags parse them
        if len(flags) > 0:
            gmt_flags += " ".join(("-{}{}".format(key, proc_flag(flag))
                                   for key, flag in flags.items()))
        
        # if we have common flags add them
        if self.common is not None:
            gmt_flags += " " + self.common
        
        if outfile is not None:
            _gmt.commands.append([gmt_exec, gmt_flags, data, outfile])
        else:
            _gmt.commands.append([gmt_exec, gmt_flags, data, self.out])
    #end f
    
    return f


def gen_tuple(cast):
    """
    Returns a function that creates a tuple of elements found in x.
    Converts x values using the passed cast function.
    Helper function for parsing command line arguments.
    """
    return lambda x: tuple(cast(elem) for elem in x.split(","))

# ***********************************************************
# * Parent argument parsers for creating command line tools *
# ***********************************************************

# Arguemnts for the raster function of the GMT object.

raster_parser = ArgumentParser(add_help=False)

raster_parser.add_argument(
    "--dpi",
    nargs="?",
    default=100,
    type=float,
    help="DPI of the output raster file.")

raster_parser.add_argument(
    "--gray",
    action="store_true",
    help="If defined output raster will be grayscaled.")

raster_parser.add_argument(
    "--portrait",
    action="store_true",
    help="If defined output raster will be in portrait format.")

raster_parser.add_argument(
    "--pagesize",
    action="store_true",
    help="If defined output eps will be created with the PageSize command.")

raster_parser.add_argument(
    "--multi_page",
    action="store_true",
    help="If defined output pdf will be multi paged.")

raster_parser.add_argument(
    "--transparent",
    action="store_true",
    help="If defined output png will be transparent.")

# Arguemnts for the raster multiplot of the GMT object.

multi_parser = ArgumentParser(add_help=False)
    
multi_parser.add_argument(
    "--nrows",
    nargs="?",
    default=None,
    type=int,
    help="Number of rows in multiplot.")

multi_parser.add_argument(
    "--top",
    nargs="?",
    default=0,
    type=float,
    help="Top margin in point units.")

multi_parser.add_argument(
    "--left",
    nargs="?",
    default=50,
    type=float,
    help="Left margin in point units.")

multi_parser.add_argument(
    "--right",
    nargs="?",
    default=125,
    type=float,
    help="Right margin in point units.")

multi_parser.add_argument(
    "--hpad",
    nargs="?",
    default=55,
    type=float,
    help="Horizontal padding between plots in point units.")

multi_parser.add_argument(
    "--vpad",
    nargs="?",
    default=100,
    type=float,
    help="Vertical padding between plots in point units.")

# Different GMT versions
_gmt_five = StrictVersion('5.0')
_gmt_five_two = StrictVersion('5.2')


_gmt_defaults_header = \
r'''#
# GMT 5.1.2 Defaults file
# vim:sw=8:ts=8:sts=8
#
'''


_gmt_defaults = {
# ********************
# * COLOR Parameters *
# ********************
"COLOR_BACKGROUND": "black",
"COLOR_FOREGROUND": "white",
"COLOR_NAN": 127.5,
"COLOR_MODEL": "none",
"COLOR_HSV_MIN_S": 1,
"COLOR_HSV_MAX_S": 0.1,
"COLOR_HSV_MIN_V": 0.3,
"COLOR_HSV_MAX_V": 1,
# ******************
# * DIR Parameters *
# ******************
"DIR_DATA": "",
"DIR_DCW": "/usr/share/gmt-dcw",
"DIR_GSHHG": "/usr/share/gmt-gshhg",
# *******************
# * FONT Parameters *
# *******************
"FONT_ANNOT_PRIMARY": "14p,Helvetica,black",
"FONT_ANNOT_SECONDARY": "16p,Helvetica,black",
"FONT_LABEL": "14p,Helvetica,black",
"FONT_LOGO": "8p,Helvetica,black",
"FONT_TITLE": "16p,Helvetica,black",
# *********************
# * FORMAT Parameters *
# *********************
"FORMAT_CLOCK_IN": "hh:mm:ss",
"FORMAT_CLOCK_OUT": "hh:mm:ss",
"FORMAT_CLOCK_MAP": "hh:mm:ss",
"FORMAT_DATE_IN": "yyyy-mm-dd",
"FORMAT_DATE_OUT": "yyyy-mm-dd",
"FORMAT_DATE_MAP": "yyyy-mm-dd",
"FORMAT_GEO_OUT": "D",
"FORMAT_GEO_MAP": "ddd:mm:ss",
"FORMAT_FLOAT_OUT": "%.12g",
"FORMAT_FLOAT_MAP": "%.12g",
"FORMAT_TIME_PRIMARY_MAP": "full",
"FORMAT_TIME_SECONDARY_MAP": "full",
"FORMAT_TIME_STAMP": "%Y %b %d %H:%M:%S",
# ********************************
# * GMT Miscellaneous Parameters *
# ********************************
"GMT_COMPATIBILITY": 4,
"GMT_CUSTOM_LIBS": "",
"GMT_EXTRAPOLATE_VAL": "NaN",
"GMT_FFT": "auto",
"GMT_HISTORY": "false",
"GMT_INTERPOLANT": "akima",
"GMT_TRIANGULATE": "Shewchuk",
"GMT_VERBOSE": "compat",
# ******************
# * I/O Parameters *
# ******************
"IO_COL_SEPARATOR": "tab",
"IO_GRIDFILE_FORMAT": "nf",
"IO_GRIDFILE_SHORTHAND": "false",
"IO_HEADER": "false",
"IO_N_HEADER_RECS": 0,
"IO_NAN_RECORDS": "pass",
"IO_NC4_CHUNK_SIZE": "auto",
"IO_NC4_DEFLATION_LEVEL": 3,
"IO_LONLAT_TOGGLE": "false",
"IO_SEGMENT_MARKER": ">",
# ******************
# * MAP Parameters *
# ******************
"MAP_ANNOT_MIN_ANGLE": "20",
"MAP_ANNOT_MIN_SPACING": "0p",
"MAP_ANNOT_OBLIQUE": 1,
"MAP_ANNOT_OFFSET_PRIMARY": "0.075i",
"MAP_ANNOT_OFFSET_SECONDARY": "0.075i",
"MAP_ANNOT_ORTHO": "we",
"MAP_DEFAULT_PEN": "default,black",
"MAP_DEGREE_SYMBOL": "ring",
"MAP_FRAME_AXES": "WSenZ",
"MAP_FRAME_PEN": "thicker,black",
"MAP_FRAME_TYPE": "fancy",
"MAP_FRAME_WIDTH": "5p",
"MAP_GRID_CROSS_SIZE_PRIMARY": "0p",
"MAP_GRID_CROSS_SIZE_SECONDARY": "0p",
"MAP_GRID_PEN_PRIMARY": "default,black",
"MAP_GRID_PEN_SECONDARY": "thinner,black",
"MAP_LABEL_OFFSET": "0.1944i",
"MAP_LINE_STEP": "0.75p",
"MAP_LOGO": "false",
"MAP_LOGO_POS": "BL/-54p/-54p",
"MAP_ORIGIN_X": "1i",
"MAP_ORIGIN_Y": "1i",
"MAP_POLAR_CAP": "85/90",
"MAP_SCALE_HEIGHT": "5p",
"MAP_TICK_LENGTH_PRIMARY": "5p/2.5p",
"MAP_TICK_LENGTH_SECONDARY": "15p/3.75p",
"MAP_TICK_PEN_PRIMARY": "thinner,black",
"MAP_TICK_PEN_SECONDARY": "thinner,black",
"MAP_TITLE_OFFSET": "14p",
"MAP_VECTOR_SHAPE": 0,
# *************************
# * Projection Parameters *
# *************************
"PROJ_AUX_LATITUDE": "authalic",
"PROJ_ELLIPSOID": "WGS-84",
"PROJ_LENGTH_UNIT": "cm",
"PROJ_MEAN_RADIUS": "authalic",
"PROJ_SCALE_FACTOR": "default",
# *************************
# * PostScript Parameters *
# *************************
"PS_CHAR_ENCODING": "ISOLatin1+",
"PS_COLOR_MODEL": "rgb",
"PS_COMMENTS": "false",
"PS_IMAGE_COMPRESS": "deflate,5",
"PS_LINE_CAP": "butt",
"PS_LINE_JOIN": "miter",
"PS_MITER_LIMIT": "35",
"PS_MEDIA": "a4",
"PS_PAGE_COLOR": "white",
"PS_PAGE_ORIENTATION": "landscape",
"PS_SCALE_X": 1,
"PS_SCALE_Y": 1,
"PS_TRANSPARENCY": "Normal",
# ****************************
# * Calendar/Time Parameters *
# ****************************
"TIME_EPOCH": "1970-01-01T00:00:00",
"TIME_IS_INTERVAL": "off",
"TIME_INTERVAL_FRACTION": 0.5,
"TIME_LANGUAGE": "us",
"TIME_UNIT": "s",
"TIME_WEEK_START": "Monday",
"TIME_Y2K_OFFSET_YEAR": 1950
}

# paper width and height in points
_gmt_paper_sizes = {
"A0":         [2380, 3368],
"A1":         [1684, 2380],
"A2":         [1190, 1684],
"A3":         [842, 1190],
"A4":         [595, 842],
"A5":         [421, 595],
"A6":         [297, 421],
"A7":         [210, 297],
"A8":         [148, 210],
"A9":         [105, 148],
"A10":        [74, 105],
"B0":         [2836, 4008],
"B1":         [2004, 2836],
"B2":         [1418, 2004],
"B3":         [1002, 1418],
"B4":         [709, 1002],
"B5":         [501, 709],
"archA":      [648, 864],
"archB":      [864, 1296],
"archC":      [1296, 1728],
"archD":      [1728, 2592],
"archE":      [2592, 3456],
"flsa":       [612, 936],
"halfletter": [396, 612],
"note":       [540, 720],
"letter":     [612, 792],
"legal":      [612, 1008],
"11x17":      [792, 1224],
"ledger":     [1224, 792],
}


# plotting functions that will use the common output filename, flags and
# the -K and -O flags
plotters = ("grdcontour", "grdimage", "grdvector", "grdview", "psbasemap",
            "psclip", "pscoast", "pscontour", "pshistogram", "psimage",
            "pslegend", "psmask", "psrose", "psscale", "pstext", "pswiggle",
            "psxy", "psxyz", "gmtlogo")

gmt_commands = ('grdcontour', 'grdimage', 'grdvector', 'grdview', 
'psbasemap', 'psclip', 'pscoast', 'pscontour', 'pshistogram', 'psimage', 
'pslegend', 'psmask', 'psrose', 'psscale', 'pstext', 'pswiggle', 'psxy', 
'psxyz', 'gmtlogo', 'blockmean', 'blockmedian', 'blockmode', 'filter1d', 
'fitcircle', 'gmt2kml', 'gmt5syntax', 'gmtconnect', 'gmtconvert', 
'gmtdefaults', 'gmtget', 'gmtinfo', 'gmtlogo', 'gmtmath', 'gmtregress', 
'gmtselect', 'gmtset', 'gmtsimplify', 'gmtspatial', 'gmtvector', 'gmtwhich',
'grd2cpt', 'grd2rgb', 'grd2xyz', 'grdblend', 'grdclip', 'grdcontour', 
'grdconvert', 'grdcut', 'grdedit', 'grdfft', 'grdfilter', 'grdgradient', 
'grdhisteq', 'grdimage', 'grdinfo', 'grdlandmask', 'grdmask', 'grdmath', 
'grdpaste', 'grdproject', 'grdraster', 'grdsample', 'grdtrack', 'grdtrend', 
'grdvector', 'grdview', 'grdvolume', 'greenspline', 'kml2gmt', 'mapproject',
'nearneighbor', 'project', 'sample1d', 'spectrum1d', 'sph2grd', 
'sphdistance', 'sphinterpolate', 'sphtriangulate', 'splitxyz', 'surface', 
'trend1d', 'trend2d', 'triangulate', 'xyz2grd')

ps2raster = {
".bmp" : "b",
".eps" : "e",
".pdf" : "f",
".jpeg": "j",
".png" : "g",
".ppm" : "m",
".tiff": "t",
}
