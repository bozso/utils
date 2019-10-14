#!/usr/bin/env python

from sys import path, argv

path.append("/home/istvan/progs/utils")

from utils import CParse, annot, pos, opt

def cast(item, caster):
    if caster is str:
        return item
    else:
        return caster(item)


class HTMLArgs(object):
    __slots__ = ("optional", "positional")
    
    def __init__(self, args=None):
        if args is None:
            args = args[1:]
        
        self.optional = {
            elem.split("=")[0]: elem.split("=")[1]
            for elem in args
            if "=" in elem 
        }
        
        self.positional = tuple(elem for elem in args if "=" not in elem)
    
    
    def pop(self, *args, **kwargs):
        type = kwargs.pop("type", str)
        
        return cast(self.pop(*args, **kwargs), type)
    
    def __getitem__(self, *args, **kwargs):
        return self.optional.__getitem__(*args, **kwargs)
    
    
    def pos(idx, type=str):
        return cast(self.positional[idx], type)


templates = {
    "imgit_float": 
    """\
    <img style="float: left; width: {img_width}"
    src="https://raw.githubusercontent.com/bozso/texfiles/master/images/{source}"
    title="{title}" alt="{title}">
    
    <div style="float: right; width: {text_width}">
        <font size="{font_size}">{title} </font>
    </div>
    """,
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


commands = {
    "imgit_float": imgit_float
}

        width=opt(help="Width of the image.", type=int, default=500),
        font_size=opt(help="Font size of title.", type=int, default=4),
        title=opt(help="Title of the image.", type=str, default=""),
        unit=opt(help="Units to use.", type=str, default="px"),
        total_width=opt(help="Total width of the page.", type=int,
                        default=1000),
        source=pos(help="Sourcefile path.", type=str)
    )


FloatOpts = namedtuple("FloatOpts", "width", "font_size"

def imgit_float(self, args):
    opts = {
        width = args.pop("width", 500, type=int)
        font_size = args.pop("fontsize", 4, type=int)
        units = args.pop("units", "px")
        total_width = args.pop("totalWidth", 1000, type=int)
        title = args.pop("title", "")
    }
    args.text_width = "%d%s" % (args.total_width - args.width , unit)
    args.img_width = "%d%s" % (args.width, unit)
    
    print(templates["imgit_float"].format(**vars(args)))


def main():
    print(argv)
    # GPP().parse().args.fun()    
    
if __name__ == "__main__":
    main()
