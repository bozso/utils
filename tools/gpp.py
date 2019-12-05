#!/usr/bin/env python

from sys import path, argv

path.append("/home/istvan/progs/utils")

from utils import new_type

def cast(item, caster):
    if caster is str:
        return item
    else:
        return caster(item)


class HTMLArgs(object):
    __slots__ = ("optional", "positional")
    
    def __init__(self, args=None):
        if args is None:
            args = argv[1:]
        
        self.optional = {
            elem.split("=")[0]: elem.split("=")[1]
            for elem in args
            if "=" in elem 
        }
        
        self.positional = tuple(elem for elem in args if "=" not in elem)
    
    
    def pop(self, *args, **kwargs):
        type = kwargs.pop("type", str)
        
        return cast(self.optional.pop(*args, **kwargs), type)
    
    def __getitem__(self, *args, **kwargs):
        return self.optional.__getitem__(*args, **kwargs)
    
    
    def pos(self, idx, type=str):
        return cast(self.positional[idx], type)


templates = {
    "imgit":
    """\
    <img style="float: left; width: {img_width}"
    src="https://raw.githubusercontent.com/bozso/texfiles/master/images/{source}"
    title="{title}" alt="{title}">
    
    <div style="float: right; width: {text_width}">
        <font size="{font_size}">{title} </font>
    </div>
    """    
}


FloatOpts = new_type("FloatOpts", "width, font_size, unit, total_width, "
                     "title, text_width, img_width, source")

def imfloat(args):
    tpl = """\
    <img style="float: left; width: {img_width}"
    src="https://raw.githubusercontent.com/bozso/texfiles/master/images/{source}"
    title="{title}" alt="{title}">
    
    <div style="float: right; width: {text_width}">
        <font size="{font_size}">{title} </font>
    </div>
    """
    
    opts = FloatOpts(
        width = args.pop("width", 500, type=int),
        font_size = args.pop("fontsize", 4, type=int),
        unit = args.pop("units", "px"),
        total_width = args.pop("totalWidth", 1000, type=int),
        title = args.pop("title", ""),
        text_width = None,
        img_width = None,
        source = None,
    )
    
    opts.text_width = "%d%s" % (opts.total_width - opts.width , opts.unit)
    opts.img_width = "%d%s" % (opts.width, opts.unit)
    opts.source = args.pos(0)
    
    return tpl.format(**opts.to_dict())


def main():
    try:
        args = HTMLArgs()
        print(imfloat(args))
    except Exception as e:
        raise TypeError("Exception caught: %s\nCalled with arguemnts: %s" % (e, argv))
        
        
    # GPP().parse().args.fun()    
    
if __name__ == "__main__":
    main()
