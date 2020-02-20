from utils import export, str_t

def parse_options(kwargs):
    if "klass" in kwargs:
        kwargs["class"] = kwargs.pop("klass")
    
    return " ".join(
        "%s=%s" % (key, val)
        if val is not True
        else "%s" % key
        for key, val in kwargs.items()
    )

class BaseTag(object):
    __slots__ = (
        "options",
    )
    
    def __init__(self, *args, **kwargs):
        self.options = kwargs
    
    
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
            name, parse_options(self.options),
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
            self.options
        )


@export
class html(Tag):
    pass

@export
class p(Tag):
    pass

@export
class div(Tag):
    pass

@export
class img(SelfClosingTag):
    pass
