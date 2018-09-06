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
    
    def addargs(self, *args):
        for arg in args:
            if arg[3] == "opt":
                if arg[4] is not None:
                    self.add_argument(
                        "--{}".format(arg[0]), "-{}".format(arg[4]),
                        help=arg[1],
                        type=arg[5],
                        default=arg[2],
                        nargs=arg[7],
                        choices=arg[6]
                    )
                else:
                    self.add_argument(
                        "--{}".format(arg[0]),
                        help=arg[1],
                        type=arg[5],
                        default=arg[2],
                        nargs=arg[7],
                        choices=arg[6]
                    )
            else:
                self.add_argument(
                    arg[0],
                    help=arg[1],
                    type=arg[5],
                    choices=arg[6]
                )
    
    def parse(self):
        return self.parse_args()
            
def newarg(name, help=None, kind="pos", alt=None, type=str, choices=None,
           default=None, nargs=None):
    
    return (name, help, default, kind, alt, type, choices, nargs)

