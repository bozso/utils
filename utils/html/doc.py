from utils.html import Children, st, Options

__all__ = (
    "Doc",
)

class Viewport(Options):
    default_values = {
        "width": "device-width",
        "initial_scale": 1.0,
    }
    
    template = "%s=%s"
    joiner = ","
    
    def __init__(self, **kwargs):
        self.options = self.default_values
        self.options.update(**kwargs) 
        
    
class Doc(Children):
    __slots__ = (
        "filename", "children", "description", "keywords", "author",
        "viewport", "encoder",
    )
    
    def __init__(self, *args, filename=None, desc="", keywords=[],
                 author="", viewport={}, encoder=None):
        
        self.filename, self.description, self.keywords, self.author, \
        self.viewport, self.encoder = (
            filename, desc, keywords, author,
            Viewport(**viewport), encoder
        )
        
        self.children = ["<!DOCTYPE html>"] + list(args)
    
    def meta(self):
        kw = self.keywords
        
        if len(kw) == 0:
            kw = ""
        else:
            kw = ",".join(kw)
        
        return (
            st.meta(charset="utf-8"),
            st.meta(name="description", content=self.description),
            st.meta(name="keywords", content=kw),
            st.meta(name="author", content=self.author),
            st.meta(name="viewport", content=self.viewport.parse_options()),
        )
    
    def append(self, *args):
        self.children.append(args)
    
    def write_to(self, writer):
        enc = self.encoder
        
        if enc is not None:
            enc.encode_children(self.children)
        
        writer.write(self.render_children())
    
    def to_file(self, filename=None):
        if filename is None:
            filename = self.filename
        
        with open(filename, "w") as f:
            self.write_to(f)
        
