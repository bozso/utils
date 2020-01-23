from __future__ import print_function, division
import os.path as pth
import base64 as b64
import json as js

from contextlib import contextmanager
from weakref import ref
from sys import argv

from .latexrun import lmain

__all__ = ("Doc", "sym", "frac", "parfrac", "twd", "tbf", "mbf", "hsp",
           "vsp", "unit", "inmath", "encode_image", "decode_image")


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
    doc("\end{%s}\n" % mode)
    

def make_begin(mode):
    def f(doc, **kwargs):
        if kwargs:
            doc("\\begin{%s}[%s]" % (mode, parse_options(kwargs)))
        else:
            doc("\\begin{%s}" % mode)
        doc.ntabs += 1
    
        yield ref(doc)()
    
        doc.ntabs -= 1
        doc("\end{%s}\n" % mode)
    
    return contextmanager(f)


class Doc(object):
    
    frame = make_begin("frame")
    center = make_begin("center")
    itemize = make_begin("itemize")
    equ = make_begin("equation")
    equs = make_begin("equation*")
    
    @classmethod
    def make_doc(cls, pyfile, texfile, **kwargs):
        if not pth.isfile(texfile):
            # TODO: replace with something
            f = open(texfile, "w"); f.close()
        
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
        self("\n\end{docuemnt}\n")
        self._texfile.close()

    
    def __call__(self, *txt):
        self._texfile.write("%s%s\n" % (self.ntabs * "\t", " ".join(txt)))

        
    def usepkg(self, pkg, **kwargs):
        if kwargs:
            self("\\usepackage[%s]{%s}" % (parse_options(kwargs), pkg))
        else:
            self("\\usepackage{%s}" % pkg)
    
    def usepkgs(self, *pkgs):
        self("\\usepackage{%s}" % ", ".join(pkg for pkg in pkgs))
        
    def biblio_style(self, style):
        self("\bibliographystyle{%s}" % style)
    
    @contextmanager
    def mode(self, mode):
        self("\mode<%s>\n{" % mode)
        self.ntabs += 1
    
        yield ref(self)()
    
        self.ntabs -= 1
        self("}\n")

    
    @contextmanager
    def begin(self, mode, **kwargs):
        if kwargs:
            self("\\begin{%s}[%s]" % (mode, parse_options(kwargs)))
        else:
            self("\\begin{%s}" % mode)
        self.ntabs += 1
    
        yield ref(self)()
    
        self.ntabs -= 1
        self("\end{%s}\n" % mode)

    @contextmanager
    def minipage(self, mode="c", width="\\textwidth", **kwargs):
        if kwargs:
            self("\\begin{minipage}[%s]{%s %s}" % (mode, width, parse_options(kwargs)))
        else:
            self("\\begin{minipage}[%s]{%s}" % (mode, width))
        self.ntabs += 1
    
        yield ref(self)()
    
        self.ntabs -= 1
        self("\\end{minipage}\n")


    
    def date(self, date):
        self("\date{%s}" % date)

    def image(self, image, **kwargs):
        if kwargs:
            self("\\includegraphics[%s]{%s}" % (parse_options(kwargs), image))
        else:
            self("\\includegraphics{%s}" % image)
    
    def newline(self):
        self("\\newline")

    def newpage(self):
        self("\\newpage")
    
    def input(self, *path):
        self("\\input{%s}" % pth.join(path))
    
    def graphics_path(self, *path):
        self("\\graphicspath{%s}" % pth.join(path))
    
    def title(self, short, long):
        self("\\title[%s]{%s}" % (short, long))

    def author(self, short, long):
        self("\\author[%s]{%s}" % (short, long))

    def institute(self, short, long):
        self("\\institute[%s]{%s}" % (short, long))
    
    def item(self, *txt):
        self("\\item %s" % " ".join(txt))
    
    
    def table_of_contents(self):
        self("\\tableofcontents")
    
    
    
    def compile(self, outfile=None, **kwargs):
        if outfile is None:
            outfile = "%s.pdf" % pth.splitext(self.texfile)[0]
        
        lmain(self.texfile, outfile=outfile, **kwargs)

    def __repr__(self):
        return "<Doc pyfile: %s, texfile: %s>" % (self.pyfile, self.texfile)

    def __str__(self):
        return "pyfile: %s\ntexfile: %s" % (self.pyfile, self.texfile)
    
    
def twd(number=None):
    if number is None:
        return "\\textwidth"
    else:
        return "%s\\textwidth" % number


def tbf(*txt):
    return "\\textbf{%s}" % " ".join(txt)


def mbf(*txt):
    return "\\mathbf{%s}" % " ".join(txt)


def hsp(number, unit="pt"):
    return "\\hspace{%s%s}" % (number, unit)

def vsp(number, unit="points"):
    return "\\vspace{%s%s}" % (number, unit)


def frac(a, b):
    return "\\frac{%s}{%s}" % (a, b)


def parfrac(a, b):
    return "\\frac{\partial %s}{\partial %s}" % (a, b)


def inmath(*txt):
    return "$ %s $" % " ".join(txt)


def encode_image(path):
    with open(path, "rb") as f:
        return b64.encodebytes(f.read()).decode("ascii")


def decode_image(obj, path, outdir=".images"):
    with open(pth.join(outdir, pth.basename(path)), "wb") as f:
        f.write(b64.b64decode(obj[path].encode("ascii")))


symbols = set(("alpha", "beta", "gamma", "partial"))
units = set(("pt", "cm"))

sym = type("Symbols", (object,),
           dict((key, "\\%s" % key) for key in symbols))

unit = type("Units", (object,),
            dict((key, "%s" % key) for key in units))
