from utils import namespace, export
from .html import Library

__all__ = [
    "libs", "plotly",
]

class JSLib(Library):
    __slots__ = (
        "_async",
    )
    
    def __init__(self, *args, **kwargs):
        self._async = bool(kwargs.get("async", True))
        
        Library.__init__(self, kwargs["path"])
    
    def add(self, doc, *args, **kwargs):
        args = set(args)
        
        if self._async:
            args.add("async")
        
        kwargs["src"] = self.path
            
        with doc.tag("script", *args, **kwargs):
            pass


libs = namespace(
    shower=JSLib(path="https://shwr.me/shower/shower.min.js"),
    mathjax=JSLib(path="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"),
)

@export
class Plotly(JSLib):
    base = "https://cdn.plot.ly/plotly-{version}.min.js"
    partial = "https://cdn.plot.ly/plotly-{partial}-{version}.min.js"
    
    def __init__(self, *args, **kwargs):
        version, partial = (
            kwargs.get("version", "latest"),
            kwargs.get("partial")
        )
        
        if partial is not None:
            path = self.partial.format(version=version, partial=partial)
        else:
            path = self.base.format(version=version)
        
        kwargs["path"] = path
        
        JSLib.__init__(self, *args, **kwargs)


plotly = namespace(
    latest=Plotly(),
    basic=Plotly(partial="base"),
    cartesian=Plotly(partial="cartesian"),
)
