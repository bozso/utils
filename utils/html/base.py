"""
HTML document generator based on https://github.com/leforestier/yattag's
simpledoc.py.
"""

import os.path as path

from utils.base import export
from utils.simpledoc import SimpleDoc, _attributes
from utils.html import encoder

__all__ = (
    "ImagePaths", "HTML", "Library",
)

class ImagePaths(object):
    __slots__ = ("paths", "doc", "width",)
    
    def __init__(self, doc, width, *paths):
        self.doc, self.width, self.paths, self.bundle = \
        doc, width, frozenset(paths), doc.bundle
    
    def search(self, name):
        m = map(lambda p: path.join(p, name), self.paths)
        f = frozenset(filter(path.isfile, m))
        l = len(f)
        
        if l == 0:
            raise RuntimeError("No image found with name '%s', "
                "in image paths: %s" % (name, self.paths)
            )
        
        if l != 1:
            raise RuntimeError("Unambigous image name '%s', "
                "image paths: %s" % (name, self.paths)
            )
        
        r, = f
        
        return r
    
    def with_title(self, path, *args, **kwargs):
        title, font_size, img_width, mode = (
            kwargs.pop("title"),
            kwargs.pop("font_size", 5.0),
            kwargs.pop("width", 500),
            kwargs.pop("mode", "top")
        )
        
        d = self.doc
        
        if mode == "side":
            d.img(style="float: left; width: %d" % int(img_width - 5),
                src=path, title=title, **kwargs)
            
            txt_width = self.width - img_width - 20
            
            # TODO: check for negative numbers
            
            with d.div(style="float: right; width: %d;" % int(txt_width)):
                d.font(title, size=font_size)
        elif mode == "top":
            d.font(title, size=font_size)
            d.img(src=path, title=title, **kwargs)
        else:
            raise TypeError("Unrecognized mode: '%s'" % mode)
        
    def img(self, name, *args, **kwargs):
        kwargs["src"] = self.search(name)
        
        self.doc.img(*args, **kwargs)

def noencode(path):
    return path


class HTML(SimpleDoc):
    __slots__ = (
        "encoder",
    )
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("stag_end", ">")
        
        if bool(kwargs.pop("bundle", False)):
            self.encoder = kwargs.pop("encoder", encoder)
        else:
            self.encoder = noencode

        SimpleDoc.__init__(self, *args, **kwargs)
    
    @staticmethod
    def presentation(*args, **kwargs):
        return Presentation(*args, **kwargs)

    def line(self, tag_name, text_content, *args, **kwargs):
        with self.tag(tag_name, *args, **kwargs):
            self.asis(text_content)

    def use(self, lib):
        lib.add(self)
    
    def math(self, txt):
        self._append("\[ %s \]" % (txt))

    def imath(self, txt):
        self._append("\( %s \)" % (txt))
    
    def image_paths(self, width, *paths):
        return ImagePaths(self, width, *paths)
    
    def youtube(self, video_id, *args, **kwargs):
        src = "https://www.youtube.com/embed/%s" % video_id
        
        kwargs["src"] = "%s?%s" % (src, proc_yt_opt(kwargs))
        
        self.iframe(*args, **kwargs)
    
    def url(self, address, txt, **kwargs):
        with self.tag("a", href=address, **kwargs):
            self.text(txt)
    
    def doi(self, number, **kwargs):
        self.url("https://doi.org/%s" % number, **kwargs)



def make_encodable(name, mode, attrib):
    if mode == "stag":
        def inner(self, *args, **kwargs):
            kwargs[attrib] = self.encoder(kwargs.pop(attrib))
            
            self.stag(name, *args, **kwargs)
    elif mode == "tag":
        def inner(self, *args, **kwargs):
            kwargs[attrib] = self.encoder(kwargs.pop(attrib))
            
            return self.tag(self, name, *args, **kwargs)
    
    return inner

encodable = {
    "img": ("stag", "src"),
    "source": ("stag", "src"),
    "link" : ("stag", "href"),
}


for enc, (mode, attrib) in encodable.items():
    setattr(HTML, enc, make_encodable(enc, mode, attrib))


########
# TAGS #
########

def make_tag(name):
    def inner(self, *args, **kwargs):
        return self.__class__.Tag(self, name, _attributes(args, kwargs))
    
    return inner

_tags = {
    "div", "head", "header", "body", "html", "center", "ul", "ol",
    "script", "style", "section", "video", "table", "tr"
}

for tag in _tags:
    setattr(HTML, tag, make_tag(tag))

#########
# STAGS #
#########

def make_stag(name):
    def inner(self, *args, **kwargs):
        return self.stag(name, *args, **kwargs)
    
    return inner

_stags = {
    "meta", "iframe",
}

for stag in _stags:
    setattr(HTML, stag, make_stag(stag))


#########
# LINES #
#########


def make_line(name):
    def inner(self, text_contents, *args, **kwargs):
        return self.line(name, text_contents, *args, **kwargs)
    
    return inner

_lines = {
    "h1", "h2", "h3", "h4", "p", "li", "b", "q", "u", "em",
    "it", "del", "strong", "th", "td", "font",
}

for line in _lines:
    setattr(HTML, line, make_line(line))

        
yt_opts = {
    "autoplay": False,
    "controls": True,
    "loop": False,
}

def proc_yt_opt(kwargs):
    return "?".join(
        kwargs.pop(key, yt_opts[key])
        for key in yt_opts
    )


class Library(object):
    __slots__ = (
        "path", "options",
    )
    
    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.options = kwargs

    
class Presentation(HTML):
    def slide(self, *args, **kwargs):
        kwargs["klass"] = "slide"
        
        return self.section(*args, **kwargs)
    
def main():
    d, tag, text = new().tagtext()
    
    with d.div(klass="asd", id="1"):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')
    
    print(d.getvalue())
    
if __name__ == "__main__":
    main()


"""
\define{\col2{in}}{<div class="column2"> \in </div>}
\define{\col3{in}}{<div class="column3"> \in </div>}
\define{\col4{in}}{<div class="column4"> \in </div>}
\define{\row{in}}{<div class="row"> \in </div>}

\define{\center{in}{args}}{<center \args> \in </center>}

\define{\style{in}{attrib}}{<div style="\attrib>" \in </div>}

\define{\pbreak}{<div class="page-break"></div>}
\define{\pbreak}{<div class="page-break"></div>}

\define{\imgit{in}{title}{attr}}{
    <img src="https://raw.githubusercontent.com/bozso/texfiles/master/images/\in"
     \attr title="\title" alt="\title"> 
    <br> \title <a href="https://raw.githubusercontent.com/bozso/texfiles/master/images/\in">
    Forrás </a>
}

\define{\imgit{in}{title}{attr}}{
    <img src="https://raw.githubusercontent.com/bozso/texfiles/master/images/geodyn/prev_work/\in"
     \attr title="\title" alt="\title"> 
    <br> <font size="4">\title </font>
}

\define{\fleft{attrib}{in}}{
    <div style="float: left; \attrib">
        \in
    </div>
}

\define{\fright{attrib}{in}}{
    <div style="float: right; \attrib">
        \in
    </div>
}

\define{\col{in}}{<div class="column"> \in </div>}
\define{\row{in}}{<div class="row"> \in </div>}
\define{\pb{in}}{<p><b>\in</b></p>}

\define{\imref{in}{title}{attr}}{<img src="\in" \attr title="\title" alt="\title"> <br> \title Forrás: <a href="in"> \in </a>}

\define{\th{in}}{<th>\in</th>}
\define{\td{in}}{<td>\in</td>}
\define{\tr{in}}{<tr>\in</tr>}

\define{\table{in}}{<table>\in</table>}
\define{\caption{in}}{<caption>\in</caption>}

\define{\with{class}{in}}{<div class="\class"> \in </div>}

\define{\bib{authors}{title}{journal}{pages}{doi}}{
    <tr valign="top">
    <td class="bibtexitem">
    \authors
    \title
     <em>\journal</em>, \pages
    \ifdef{doi}
        [&nbsp;<a href="\doi">DOI</a>&nbsp;]
    \endif
    </td>
    </tr>
}
"""
