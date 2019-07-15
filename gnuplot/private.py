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

from sys import platform, stderr
from os import linesep, popen, remove
from numpy import dtype
from math import ceil, sqrt
from weakref import ref
import subprocess as sub
    
    
class MultiPlot(object):
    def __init__(self, nplot, session, **kwargs):
        self.session = ref(session)()
        
        common_keys = bool(kwargs.get("ckeys", False))
        
        if common_keys:
            nplot += 1
        
        self.nplot = nplot
        self.left = float(kwargs.get("left", 20)) / 100.0
        self.between = float(kwargs.get("between", 20.0)) / 100.0
        self.width = float(kwargs.get("width", 30.0)) / 100.0
        self.key_height = float(kwargs.get("key_height", 50.0)) / 100.0
        
        self.width_total = self.width * nplot + self.between * (nplot - 1) \
                           + self.left + self.key_height
        
        nrows = kwargs.get("nrows", None)
        
        if nrows is None:
            nrows = max([1, ceil(sqrt(self.nplot) - 1)])
        
        ncols = ceil(self.nplot / nrows)
        
        portrait = kwargs.get("portrait", False)
        
        if portrait and ncols > nrows:
            nrows, ncols = ncols, nrows
        elif nrows > ncols:
            nrows, ncols = ncols, nrows
        
        self.nrows, self.ncols = nrows, ncols

        order = kwargs.get("order", "rowsfirst")
        title = kwargs.get("title", None)
        
        if title is not None:
            txt = "set multiplot layout {},{} {} title '{}'"\
                  .format(nrows, ncols, order, title)
        else:
            txt = "set multiplot layout {},{} {}".format(nrows, ncols, order)
        
        if common_keys:
            txt += "; unset key"
        
        self.session(txt)
    
    
    def __call__(self, *args):
        self.session(*args)
    
    
    def key(self, *titles):
        self("unset title")
    
        plot = ", ".join("2 title '%s'" % title for title in titles)
        
        self(
        """
        set lmargin at screen %g
        set rmargin at screen 1
        set key center center
        set border 0
        unset tics
        unset xlabel
        unset ylabel
        set yrange [0:1]
        plot %s
        """ % (self.margins(self.nplot)[0] - 0.35, plot))
    
    
    def plot(self, ii, txt):
        sess = self.session
        
        if ii > 0:
            self("unset ylabel")
        
        self("set lmargin at screen %g\nset rmargin at screen %g" % self.margins(ii))
        sess(txt)
    
    
    def margins(self, ii):
        l, b, w = self.left, self.between, self.width
        left = ii * (w + b) + l
        return left, left + w

    
    def __del__(self):
        self.session("unset multiplot")
        self.session.multi = None


#if platform == "mac":
    #from gnuplot_platforms import GnuplotProcessMac as gpp

#elif platform == "win32" or platform == "cli":
    #from gnuplot_platforms import GnuplotProcessWin32 as gpp

#elif platform == "darwin":
    #from gnuplot_platforms import GnuplotProcessMacOSX as gpp

#elif platform[:4] == "java":
    #from gnuplot_platforms import GnuplotProcessJava as gpp

#elif platform == "cygwin":
    #from gnuplot_platforms import GnuplotProcessCygwin as gpp

#else:
    #from gnuplot_platforms import GnuplotProcessUnix as gpp
