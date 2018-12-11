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

from utils.gnuplot import linedef
import numpy as np

def plot_scatter(gp, data, ncols, out=None, title=None, idx=None, titles=None,
                 palette="rgb", endian="default", portrait=False):
    
    binary = "%double" * (ncols + 2)
    
    if idx is None:
        idx = range(ncols)
    
    # parse titles
    if titles is None:
        titles = range(1, ncols + 1)
        
    gp.binary("format='{}' endian={}".format(binary, endian))
    
    # gp.palette(palette)
    # gp.colorbar(cbfomat="%4.2f")
    # gp.unset("colorbox")
    
    return (gp.infile(data, binary=binary, endian=endian,
                      using="1:2:{}".format(ii + 3),
                      vith=linedef("points", pt="dot", palette=True))
            for ii in idx)
    

def groupby_plot(gp, x, y, data, by, colors, **kwargs):
    fields = np.unique(data[by])
    
    
    indices = (np.where(data[by] == field) for field in fields)
    ldefs = (linedef("points", rgb=cols[color], **kwargs) for color in colors)
    
    return (gp.data(data[x][idx], data[y][idx], vith=ldef,
            title="{} {}".format(by, field))
            for field, idx, ldef in zip(fields, indices, ldefs))
