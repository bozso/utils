from __future__ import print_function, division
import os.path as pth
from contextlib import contextmanager
from weakref import ref

def parse_options(kwargs):
    return " ".join("%s=%s" % (key, str(value))
                    for key, value in kwargs.items())





class Doc(object):
    def __init__(self, pyfile, texfile, klass="plain", **kwargs):
        if pyfile > texfile:
            self = None
            return

        self.texfile = texfile
        self.pyfile = pyfile
        self.ntabs = 0
        
        self._texfile = open(texfile, "w")
        
        if kwargs:
            self._texfile.write("\documentclass[%s]{%s}\n"
                                % (parse_options(kwargs), klass))
        else:
            self._texfile.write("\documentclass{%s}\n" %  klass)


    def __call__(self, txt):
        self._texfile.write("%s%s\n" % (self.ntabs * "\t", txt))

        
    def usepkg(self, pkg, **kwargs):
        if kwargs:
            self("\\usepackage[%s]{%s}" % (parse_options(kwargs), pkg))
        else:
            self("\\usepackage{%s}" % pkg)

    def biblio_style(self, style):
        self("\bibliographystyle{%s}" % style)
    
    
    @contextmanager
    def mode(self, mode):
        self("\mode<%s>\n{" % mode)
        self.ntabs += 1
    
        yield ref(self)()
    
        self.ntabs -= 1
        self("}")
    
    
    
    
    @contextmanager
    def begin(self, mode, **kwargs):
        if kwargs:
            self("\\begin{%s}[%s]" % (mode, parse_options(kwargs)))
        else:
            self("\\begin{%s}" % mode)
        self.ntabs += 1
    
        yield ref(self)()
    
        self.ntabs -= 1
        self("\end{%s}" % mode)
    
    @contextmanager
    def frame(self, **kwargs):
        self.begin("frame", **kwargs)
    
    def date(self, date):
        self("\date{%s}" % date)
    
    def __del__(self):
        self._texfile.close()

