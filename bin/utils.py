#!/usr/bin/env python

from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split
from os import mkdir, path as pth
from argparse import ArgumentParser
from textwrap import fill
from glob import iglob

__all__ = ("cmd", "argp")


home_path = pth.expanduser("~")
screenap_dir = pth.join(home_path, "screencaps")


if not pth.isdir(screenap_dir):
    mkdir(screenap_dir)


def cmd(command, *args, **kwargs):
    debug = kwargs.pop("debug", False)
    
    Cmd = "%s %s" % (command, " ".join(str(arg) for arg in args))
    
    if debug:
        print(Cmd)
        return
    
    try:
        proc = check_output(split(Cmd), stderr=STDOUT)
    except CalledProcessError as e:
        log.error("\nNon zero returncode from command: \n'{}'\n"
                  "\nOUTPUT OF THE COMMAND: \n\n{}\nRETURNCODE was: {}"
                  .format(Cmd, e.output.decode(), e.returncode))

        raise e

    return proc


class Argp(ArgumentParser):
    def __init__(self, **kwargs):
        subcmd = bool(kwargs.pop("subcmd", False))
        
        ArgumentParser.__init__(self, **kwargs)
        
        if subcmd:
            self.subparser = self.add_subparsers(**kwargs)
        else:
            self.subparser = None
        
    
    def addargs(self, *args):
        for arg in args:
            gp.ap_add_arg(self, arg)

    
    def subp(self, **kwargs):
        if self.subparser is None:
            self.subparser = self.add_subparsers(**kwargs)
        else:
            raise ValueError("One subparser is already initiated!")
    
    
    def subcmd(self, name, fun, *args, **kwargs):
        
        subtmp = self.subparser.add_parser(name, **kwargs)
        
        for arg in args:
            gp.ap_add_arg(subtmp,  arg)
        
        subtmp.set_defaults(fun=fun)

    
    @staticmethod
    def narg(name, help=None, kind="opt", alt=None, type=str, choices=None,
             default=None, nargs=None):
        return (name, help, default, kind, alt, type, choices, nargs)


def _ap_add_arg(obj, arg):
    if arg[3] == "opt":
        if arg[4] is not None:
            obj.add_argument(
                "--{}".format(arg[0]), "-{}".format(arg[4]),
                help=arg[1],
                type=arg[5],
                default=arg[2],
                nargs=arg[7],
                choices=arg[6])
        else:
            obj.add_argument(
                "--{}".format(arg[0]),
                help=arg[1],
                type=arg[5],
                default=arg[2],
                nargs=arg[7],
                choices=arg[6])
    elif arg[3] == "pos":
        obj.add_argument(
            arg[0],
            help=arg[1],
            type=arg[5],
            choices=arg[6])
    
    elif arg[3] == "flag":
        obj.add_argument(
            "--{}".format(arg[0]),
            help=arg[1],
            action="store_true")


def screencap(args):
    pngs = tuple(int(pth.splitext(pth.basename(png))[0])
                     for png in iglob(pth.join(screenap_dir, "*.png")))
    
    if pngs:
        last = max(pngs)
    else:
        last = -1
    
    cmd("import", pth.join(screenap_dir, "%d.png" % (last + 1)))


def merge_caps(args):
    pass

def main():
    
    ap = Argp(subcmd=True)
    
    ap.subcmd("screencap", screencap)
    
    args = ap.parse_args()
    args.fun(args)
    

if __name__ == "__main__":
    main()
