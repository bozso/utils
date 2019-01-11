from __future__ import print_function, division
import os.path as pth
from contextlib import contextmanager
from weakref import ref

def parse_options(kwargs):
    return " ".join("%s=%s" % (key, str(value))
                    for key, value in kwargs.items())


@contextmanager
def begin(doc, mode, **kwargs):
    if kwargs:
        doc("\\begin{%s}[%s]" % (mode, parse_options(kwargs)))
    else:
        doc("\\begin{%s}" % mode)
    doc.ntabs += 1

    yield ref(doc)()

    doc.ntabs -= 1
    doc("\end{%s}" % mode)
    

def make_begin(mode):
    def f(doc, **kwargs):
        if kwargs:
            doc("\\begin{%s}[%s]" % (mode, parse_options(kwargs)))
        else:
            doc("\\begin{%s}" % mode)
        doc.ntabs += 1
    
        yield ref(doc)()
    
        doc.ntabs -= 1
        doc("\end{%s}" % mode)
    
    return contextmanager(f)


class Doc(object):
    
    frame = make_begin("frame")
    center = make_begin("center")
    minipage = make_begin("minipage")
    
    @classmethod
    def make_doc(cls, pyfile, texfile, **kwargs):
        if pth.getmtime(pyfile) <= pth.getmtime(texfile):
            return None
        else:
            return cls(pyfile, texfile, **kwargs)
    
    def __init__(self, pyfile, texfile, klass="plain", **kwargs):
        self.texfile = texfile
        self.pyfile = pyfile
        self.ntabs = 0
        
        self._texfile = open(texfile, "w")
        
        if kwargs:
            self._texfile.write("\documentclass[%s]{%s}\n"
                                % (parse_options(kwargs), klass))
        else:
            self._texfile.write("\documentclass{%s}\n" %  klass)
    
    def start(self):
        self("\n\n\\begin{document}\n\n")


    def __del__(self):
        if self is not None:
            self("\n\end{docuemnt}\n")
            self._texfile.close()

    
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
    
    def date(self, date):
        self("\date{%s}" % date)

