"""
HTML document generator based on https://github.com/leforestier/yattag's
simpledoc.py.
"""

__all__ = (
    "new",
)


class DocError(Exception):
    pass

class Tag(object):
    __slots__ = (
        "doc", "name", "attrs", "position", "parent_tag", "attrs",
    )
    
    def __init__(self, doc, name, attrs): # name is the tag name (ex: 'div')
        # type: (SimpleDoc, str, Dict[str, Union[str, int, float]]) -> None
        
        print(doc, name, attrs)
        
        self.doc = doc
        self.name = name
        self.attrs = attrs
        self.parent_tag, self.position, self.attrs = None, None, None

    def __enter__(self):
        # type: () -> None
        self.parent_tag = self.doc.current_tag
        self.doc.current_tag = self
        self.position = len(self.doc.result)
        self.doc._append('')

    def __exit__(self, tpe, value, traceback):
        # type: (Any, Any, Any) -> None
        
        if value is None:
            if self.attrs:
                self.doc.result[self.position] = "<%s %s>" % (
                    self.name,
                    dict_to_attrs(self.attrs),
                )
            else:
                self.doc.result[self.position] = "<%s>" % self.name
            
            self.doc._append("</%s>" % self.name)
            self.doc.current_tag = self.parent_tag


class HTMLDoc(object):
    __slots__ = (
        "outfile", "result", "current_tag", "_append", "_stag_end",
        "_br", "_nl2br",
    )

    class DocumentRoot(object):

        class DocumentRootError(DocError, AttributeError):
            # Raising an AttributeError on __getattr__ instead of just a DocError makes it compatible
            # with the pickle module (some users asked for pickling of SimpleDoc instances).
            # I also keep the DocError from earlier versions to avoid possible compatibility issues
            # with existing code.
            pass

        def __getattr__(self, item):
            # type: (str) -> Any
            raise SimpleDoc.DocumentRoot.DocumentRootError("DocumentRoot here. You can't access anything here.")
    
    def __init__(self, *args, **kwargs):
        self.result = [] # type: List[str]
        self.current_tag = self.__class__.DocumentRoot() # type: Any
        self._append = self.result.append
        
        stag_end = kwargs.get("stag_end", " />")
        
        self._stag_end = stag_end
        self._br = '<br' + stag_end
        self._nl2br = bool(kwargs.get("nl2br", False))
    
    def tag(self, tag_name, *args, **kwargs):
        return Tag(self, tag_name, _attributes(args, kwargs))

    def line(self, tag_name, text_content, *args, **kwargs):
        with self.tag(tag_name, *args, **kwargs):
            self.text(text_content)

    def stag(self, tag_name, *args, **kwargs):
        if args or kwargs:
            self._append("<%s %s>" % (
                tag_name,
                dict_to_attrs(_attributes(args, kwargs)),
                # self._stag_end
            ))
        else:
            self._append("<%s%s" % (tag_name, self._stag_end))


    def tagtext(self):
        return self, self.tag, self.text

    def nl(self):
        # type: () -> None
        self._append('\n')

    def getvalue(self):
        return "".join(self.result)

    def text(self, *strgs):
        for strg in strgs:
            transformed_string = html_escape(strg)
            if self._nl2br:
                self._append(
                    self.__class__._newline_rgx.sub(
                        self._br,
                        transformed_string
                    )
                )
            else:
                self._append(transformed_string)

        
def html_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s, (int, float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except AttributeError:
        raise TypeError(
            "You can only insert a string, an int or a float inside "
            "a xml/html text node. Got %s (type %s) instead." % 
            (repr(s), repr(type(s)))
        )


def attr_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s,(int,float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    except AttributeError:
        raise TypeError(
            "xml/html attributes should be passed as strings, "
            "ints or floats. Got %s (type %s) instead." %
            (repr(s), repr(type(s)))
        )

def dict_to_attrs(dct):
    # type: (Dict[str, Any]) -> str
    return ' '.join(
        (key if value is ATTR_NO_VALUE
        else '%s="%s"' % (key, attr_escape(value)))
        for key, value in dct.items()
    )

def _attributes(args, kwargs):
    # type: (Any, Any) -> Dict[str, Any]
    lst = [] # type: List[Any]
    append = lst.append
    
    for arg in args:
        if isinstance(arg, tuple):
            append(arg)
        elif isinstance(arg, str):
            append((arg, ATTR_NO_VALUE))
        else:
            raise ValueError(
                "Couldn't make a XML or HTML attribute/value pair "
                "out of %s." % repr(arg)
            )
    
    result = dict(lst)
    
    result.update(
        (('class', value) if key == 'klass' else (key, value))
        for key,value in kwargs.items()
    )
    
    return result


ATTR_NO_VALUE = object()

def make_tag(name):
    def inner(self, *args, **kwargs):
        return Tag(self, name, _attributes(args, kwargs))
    
    return inner

tags = {"h1", "h2", "h3", "h4", "p", "div"}

for tag in tags:
    setattr(HTMLDoc, tag, make_tag(tag))


def new(*args, **kwargs):
    return HTMLDoc(*args, **kwargs)

def main():
    d, tag, text = new().tagtext()
    
    with d.div(klass="asd", id="1"):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')
    
    print(d.getvalue())
    
if __name__ == "__main__":
    main()
