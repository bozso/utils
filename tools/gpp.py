#!/usr/bin/env python

from sys import path

path.append("/home/istvan/progs/utils")

from utils import CParse, annot, pos, opt

templates = {
    "imgit_float": 
    """\
    <img style="float: left; width: {img_width}"
    src="https://raw.githubusercontent.com/bozso/texfiles/master/images/{source}"
    title="{title}" alt="{title}">
    
    <div style="float: right; width: {text_width}">
        <font size="{font_size}">{title} </font>
    </div>
    """
}



class GPP(CParse):
    commands = ("imgit_float",)
    
    @annot(
        width=opt(help="Width of the image.", type=int, default=500),
        font_size=opt(help="Font size of title.", type=int, default=4),
        title=opt(help="Title of the image.", type=str, default=""),
        unit=opt(help="Units to use.", type=str, default="px"),
        total_width=opt(help="Total width of the page.", type=int,
                        default=1000),
        source=pos(help="Sourcefile path.", type=str)
    )
    def imgit_float(self):
        args = self.args
        unit = self.args.unit
        
        args.text_width = "%d%s" % (args.total_width - args.width , unit)
        args.img_width = "%d%s" % (args.width, unit)
        
        print(templates["imgit_float"].format(**vars(args)))


def main():
    GPP().parse().args.fun()    
    
if __name__ == "__main__":
    main()
