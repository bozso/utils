from common import *

__all__ = [
    "run",
    "select",
    "inp",
    "password"
]


opt = "-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"
bin = "dmenu %s" % opt


def parse_opts(**kwargs):
    return " ".join('-%s "%s"' % (key, value)
                    for key, value in kwargs.items())


def run(choices=None, **kwargs):
    cmd = "%s %s" % (bin, parse_opts(**kwargs))
    
    if choices is not None:
        p = Popen(split(cmd), stdin=PIPE, stdout=PIPE)
        out, err = p.communicate(choices)
    else:
        p = Popen(split(cmd), stdout=PIPE)
        out, err = p.communicate()
        
    if p.returncode != 0:
        raise RuntimeError("None zero returncode!")
    
    return out.decode()
    

def select(*args, **kwargs):
    p = kwargs.pop("p", None)
    
    choices = b"\n".join(key.encode("ascii") for key in kwargs.keys())
    
    if len(args) > 0:
        choices = \
        b"\n".join((choices, b"\n".join(elem.encode("ascii")
                    for elem in args)))
    
    key = run(choices=choices.strip(), p=p).strip("\n").strip()
    
    return key


def inp(**kwargs):
    cmd = "%s %s" % (bin, parse_opts(**kwargs))
    
    p = Popen(split(cmd), stdin=PIPE, stdout=PIPE)
    out, err = p.communicate()
    p.stdin.close()
    
    if p.returncode != 0:
        raise RuntimeError("None zero returncode!")
    
    return out.decode().strip("\n").strip()

    
def password(**kwargs):
    kwargs.update({
        "nf": "black",
        "nb": "black"
    })
    
    return inp(**kwargs)
