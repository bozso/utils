# Utils

## gnuplot.py

I have discovered [gnuplot-py](http://gnuplot-py.sourceforge.net/) not so long
ago and I wanted to use it as a simple python wrapper to gnuplot. However
I have found the gnuplot-py interface to be overly complicated and hard to
debug. Plus it was designed with Python 2 and did not really work with
Python 3.

Based on gnuplot-py I have written my own package. This is still in early
developement so be careful with it if you want to try it out. It should work
with Python 2.7+ and Python 3+.

At the moment it is only necessary to use the `gnuplot.py` file to be able
to use the wrapper. I think you can only use gnuplot on a Unix system in
the future I will properly implement `gnuplot_platforms.py` module to support
all platforms (Windows, Mac, Linux).

If you have found any bugs or have any suggestions feel free to contact me.

## Acknowledgement

I took a couple of code snippets and concepts from
[gnuplot-py](http://gnuplot-py.sourceforge.net/).
