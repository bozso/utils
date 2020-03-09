from utils import namespace
from utils.html import Library, st

__all__ = (
    "css",
)

class CSSLib(Library):
    def __init__(self, path, *args, **kwargs):
        Library.__init__(self, path, *args, **kwargs)
        
    
    def add(self, *args, **kwargs):
        kwargs.update(self.options)
        
        kwargs["rel"] = "stylesheet"
        kwargs["href"] = self.path
        
        return st.link(**kwargs)



css = namespace(
    bootstrap = CSSLib(
        "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css",
        integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh",
        crossorigin="anonymous",
    ),
)
