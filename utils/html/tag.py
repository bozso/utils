from utils import str_t, namespace, isiter
from inspect import isgenerator

__all__ = (
    "tags", "t", "stags", "st", "Children", "Options", "url", "doi",
)


class TagFactory(object):
    __slots__ = (
        "options", "obj",
    )
    
    def __init__(self, obj, **kwargs):
        self.options, self.obj = kwargs, obj
    
    def __call__(self, *args):
        return obj(*args, **self.options)
    

class Options(object):
    template = '%s="%s"'
    joiner = " "
    
    def parse_options(self):
        opts, tpl = self.options, self.template
        
        if "klass" in opts:
            opts["class"] = opts.pop("klass")
        
        return self.joiner.join(
            tpl % (key, val)
            if val is not True
            else "%s" % key
            for key, val in opts.items()
        )


class BaseTag(Options):
    __slots__ = (
        "options",
    )
    
    encode = None
    
    def __init__(self, *args, **kwargs):
        self.options = kwargs
    
    @classmethod
    def With(cls, **kwargs):
        return TagFactory(cls, **kwargs)
    

class Children(object):
    def __call__(self, *items):
        if isgenerator(items[0]):
            items = tuple(items[0])
        
        self.children.extend(items)
        
    def append(self, item):
        self.children.append(item)
    
    # @staticmethod
    # def sum_impl(self):
        # for child in self.children:
            # try:
                
    
    def render_children(self):
        return "".join(
            child.render()
            if not isinstance(child, str_t)
            else str(child)
            for child in self.children
        )


class Tag(BaseTag, Children):
    __slots__ = (
        "children",
    )
    
    def __init__(self, *args, **kwargs):
        BaseTag.__init__(self, *args, **kwargs)
        self.children = list(args)
    
    def render(self):
        name = self.name
        
        return "<%s %s>%s</%s>" % (
            name, self.parse_options(),
            self.render_children(), name
        )
    
class SelfClosingTag(BaseTag):
    def render(self):
        return "<%s %s>" % (
            self.name,
            self.parse_options()
        )


_tags = {
    "a", "abbr", "acronym", "address", "applet", "article", "aside",
    "audio", "b", "bdi", "bdo", "big", "body", "button", "canvas",
    "caption",
    # TODO: deprecation warning
    "center",
    "cite", "code", "colgroup", "data", "dd", "del", "details",
    "dfn", "dialog",
    # TODO: deprecation warning
    "dir",
    "div", "dl", "dt", "em", "fieldset", "figcaption", "figure",
    "font", "footer", "form", "frameset", "head", "header", 
    "html", "i", "iframe", "ins", "kbd", "label", "legend",
    "li", "main", "map", "mark", "meter", "nav", "noframes",
    "noscript", "object", "ol", "optgroup", "option", "output",
    "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby",
    "s", "samp", "script", "section", "select", "small", "span",
    "strike", "strong", "style", "sub", "summary", "sup",
    "svg", "table", "tbody", "td", "template", "textarea",
    "tfoot", "th", "thead", "time", "title", "tr", "tt", "u",
    "ul", "var", "video", "wbr",
}

_tags |= {"h%d" % ii for ii in range(1, 7)}


tags = namespace(_name_="Tags",
    **{
        key: type(key, (Tag,), {"name": key})
        for key in _tags
    }
)

t = tags

_stags = {
    "area", "base", "basefont", "col", "embed", "frame", "meta", "img",
    "input", "link", "meta", "param", "source", "track",
    
}

stags = namespace(_name_="SelfClosingTags",
    **{
        key: type(key, (SelfClosingTag,), {"name": key})
        for key in _stags
    }
)

stags.img.encode = "src"
stags.source.encode = "src"
stags.link.encode = "href"

st = stags

def url(address, txt, **kwargs):
    return t.a(txt, href=address, **kwargs)

def doi(number, **kwargs):
    return url("https://doi.org/%s" % number, **kwargs)


symbols = namespace(
    linebreak = "<br>",
    thematic_break = "<hr>",
)
