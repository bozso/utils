"""
HTML document generator based on https://github.com/leforestier/yattag's
simpledoc.py.
"""

import base64

from utils.utils import export
from utils.simpledoc import SimpleDoc, _attributes

__all__ = [
    "jslibs", 
]

########
# TAGS #
########

def make_tag(name):
    def inner(self, *args, **kwargs):
        return self.__class__.Tag(self, name, _attributes(args, kwargs))
    
    return inner

tags = {
    "div", "head", "header", "body", "html", "center", "ul", "ol",
    "script", "style", "section", "video", "table", "tr"
}

for tag in tags:
    setattr(SimpleDoc, tag, make_tag(tag))

#########
# STAGS #
#########

def make_stag(name):
    def inner(self, *args, **kwargs):
        return self.stag(name, *args, **kwargs)
    
    return inner

stags = {
    "meta", "link", "source", "iframe",
}

for stag in stags:
    setattr(SimpleDoc, stag, make_stag(stag))


#########
# LINES #
#########


def make_line(name):
    def inner(self, text_contents, *args, **kwargs):
        return self.line(name, text_contents, *args, **kwargs)
    
    return inner

lines = {
    "h1", "h2", "h3", "h4", "p", "li", "bold", "q", "u", "em",
    "it", "del", "strong", "th", "td", "font",
}

for line in lines:
    setattr(SimpleDoc, line, make_line(line))


class Encoder(object):
    __slots__ = (
        "encoder",
    )
    
    klass2ext = {
        "text" : frozenset({
            "js", "css",
        }),
        
        "video" : frozenset({
            "mp4",
        }),
        
        "image": frozenset({
            "png", "jpg",
        }),
    }
    
    tpl = "data:{klass}/{mode};charset=utf-8;base64,{data}"
    
    ext2klass = {v: k for k, v in klass2ext.items()}
    
    convert = {
        "js": "javascript",
    }
    
    def __init__(self, *args, **kwargs):
        self.encoder = kwargs.get("encoder", base64.b64encode)

    
    def __call__(self, media_path):
        mode = ext = path.splitext(media_path)[1].strip(".")
        
        for key, val in self.ext2klass.items():
            if ext in key:
                klass = val
                break
        
        if mode in self.convert:
            mode = convert[ext]
        
        with open(media_path, "rb") as f:
            data = self.encoder(f.read())
        
        return self.tpl.format(
            klass=klass, mode=mode, data=data.decode("utf-8")
        )


encoder = Encoder()

encodable = {
    "img", "video",
}

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


@export
class HTML(SimpleDoc):
    __slots__ = (
        "bundle", "encoder",
    )
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("stag_end", ">")
        
        self.bundle, self.encoder = (
            bool(kwargs.pop("bundle", False)),
            kwargs.pop("encoder", encoder),
        )
        
        SimpleDoc.__init__(self, *args, **kwargs)
    
    @staticmethod
    def presentation(*args, **kwargs):
        return Presentation(*args, **kwargs)

    def use(self, lib):
        lib.add(self)
    
    def math(self, txt):
        self._append("\[ %s \]" % (txt))

    def imath(self, txt):
        self._append("\( %s \)" % (txt))

    def img(self, *args, **kwargs):
        path = kwargs.pop("src")
        
        if self.bundle:
            src = self.encoder(path)
        else:
            src = path
        
        kwargs["src"] = src
        
        self.stag("img", *args, **kwargs)
    
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
        "path",
    )
    
    def __init__(self, path):
        self.path = path
    

class CSSLib(Library):
    pass
    

class JSLib(Library):
    __slots__ = (
        "_async",
    )
    
    def __init__(self, *args, **kwargs):
        self._async = bool(kwargs.get("async", True))
        Library.__init__(self, kwargs["path"])
    
    def add(self, doc):
        if self._async:
            with doc.tag("script", "async", src=self.path):
                pass
        else:
            with doc.tag("script", src=self.path):
                pass


jslibs = type("JSLibs", (object,), {
    "shower": JSLib(path="https://shwr.me/shower/shower.min.js"),
    "mathjax": JSLib(path="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"),
    "plotly": JSLib(path="https://cdn.plot.ly/plotly-latest.min.js"),
})


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
