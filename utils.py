from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split
import argparse as ap

def cmd(Cmd, debug=False):
    """
    Calls a command line program. See documentation of modules for arguments.
    
    Parameters
    ----------
    Cmd : str
        Command string to be executed.
    
    Returns
    -------
    ret : byte-string
        Output of called module.
    
    Raises
    ------
    CalledProcessError
        If something went wrong with the calling of the module, e.g.
        non zero returncode.

    Examples
    --------
    
    >>> from utils.git import cmd
    >>> cmd("ls *.png *.txt")
    """
    
    if debug:
        print(Cmd)
        return None
    
    try:
        cmd_out = check_output(split(Cmd), stderr=STDOUT)

    except CalledProcessError as e:
        print("ERROR: Non zero returncode from command: '{}'".format(Cmd))
        print("OUTPUT OF THE COMMAND: \n{}".format(e.output.decode()))
        print("RETURNCODE was: {}".format(e.returncode))
        
        raise e
        
    return cmd_out

class argp(ap.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subp = None
        
    def addargs(self, *args):
        for arg in args:
            _ap_add_arg(self, arg)

    def subp(**kwargs):
        if self.subp is None:
            self.subp = self.add_subparsers(**kwargs)
    
    def subcmd(self, name, fun, *args, **kwargs):
        
        subtmp = self.subp.add_parser(name, **kwargs)
        
        for arg in args:
            _ap_add_arg(subtmp, arg)
        
        subtmp.set_defaults(func=fun)
        
def narg(name, help=None, kind="pos", alt=None, type=str, choices=None,
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
                choices=arg[6]
            )
        else:
            obj.add_argument(
                "--{}".format(arg[0]),
                help=arg[1],
                type=arg[5],
                default=arg[2],
                nargs=arg[7],
                choices=arg[6]
            )
    else:
        obj.add_argument(
            arg[0],
            help=arg[1],
            type=arg[5],
            choices=arg[6]
        )
