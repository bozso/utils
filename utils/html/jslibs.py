from utils import namespace
from utils.html import Library, t

__all__ = (
    "libs", "plotly", "Plotly",
)

class JSLib(Library):
    __slots__ = (
        "_async",
    )
    
    def __init__(self, *args, **kwargs):
        self._async = bool(kwargs.get("async", True))
        
        Library.__init__(self, kwargs["path"])
    
    def add(self, *args, **kwargs):
        args = set(args)
        
        if self._async:
            args.add("async")
        
        kwargs["src"] = self.path
        
        return t.script(**kwargs)


libs = namespace(
    shower=JSLib(path="https://shwr.me/shower/shower.min.js"),
    mathjax=JSLib(path="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"),
    jquery=JSLib(path="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"),
)

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
