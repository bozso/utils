from utils import str_t, namespace

__all__ = (
    "tags", "t", "stags", "st",
)


class BaseTag(object):
    __slots__ = (
        "options",
    )
    
    def __init__(self, *args, **kwargs):
        self.options = kwargs
    
    def parse_options(self):
        opts = self.options
        
        if "klass" in opts:
            opts["class"] = opts.pop("klass")
        
        return " ".join(
            "%s=%s" % (key, val)
            if val is not True
            else "%s" % key
            for key, val in opts.items()
        )

    
class Tag(BaseTag):
    __slots__ = (
        "children",
    )
    
    def __init__(self, *args, **kwargs):
        BaseTag.__init__(self, *args, **kwargs)
        self.children = args
        
    
    def render(self):
        name = self.__class__.__name__
        
        return "<%s %s>%s</%s>" % (
            name, self.parse_options(),
            self.render_children(), name
        )
    
    def render_children(self):
        return "".join(
            child.render()
            if not isinstance(child, str_t)
            else str(child)
            for child in self.children
        )


class SelfClosingTag(BaseTag):
    def render(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            self.parse_options()
        )


tags = {
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

tags |= {"h%d" % ii for ii in range(1, 7)}


tags = namespace(_name_="Tags",
    **{
        key: type(key, (Tag,), {})
        for key in tags
    }
)

t = tags

stags = {
    "area", "base", "basefont", "col", "embed", "frame", "img",
    "input", "link", "meta", "param", "source", "track",
    
}

stags = namespace(_name_="SelfClosingTags",
    **{
        key: type(key, (Tag,), {})
        for key in stags
    }
)

st = stags

symbols = namespace(
    linebreak = "<br>",
    thematic_break = "<hr>",
)
