from utils import namespace
from utils.html import Library, t

__all__ = (
    "js", "plotly", "Plotly",
)

class JSLib(Library):
    __slots__ = (
        "_async",
    )
    
    def __init__(self, path, *args, **kwargs):
        self._async = bool(kwargs.get("_async_", True))
        
        Library.__init__(self, path, *args, **kwargs)
    
    def add(self, **kwargs):
        kwargs.update(self.options)
        
        if self._async:
            kwargs["async"] = True
        
        kwargs["src"] = self.path
        
        return t.script(**kwargs)


js = namespace(
    shower=JSLib(path="https://shwr.me/shower/shower.min.js"),
    mathjax=JSLib(path="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"),
    jquery=JSLib(path="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"),
    bootstrap = JSLib(
        path="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
        integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6",
        crossorigin="anonymous",
        _async_=False,
    ),
    bs_jquery=JSLib(
        path="https://code.jquery.com/jquery-3.4.1.slim.min.js",
        integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n",
        crossorigin="anonymous",
        _async_=False,
    ),
    bs_popper = JSLib(
        path="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
        integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo",
        crossorigin="anonymous",
        _async_=False,
    ),
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
        
        JSLib.__init__(self, path, *args, **kwargs)


plotly = namespace(
    latest=Plotly(),
    basic=Plotly(partial="base"),
    cartesian=Plotly(partial="cartesian"),
)
