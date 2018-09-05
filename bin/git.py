#! /usr/bin/env python

from argparse import ArgumentParser
from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split
import plac_core as pl

commands = "compush", "add", "pull"

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

@pl.annotations(message=("Commit message.", "option"))
def compush(message):
    cmd("git commit -am \"{}\"".format(message))
    cmd("git push origin master")

@pl.annotations(files=("List of files to add."))
def add(files):
    cmd("git add {}".format(" ".join(args.files)))

def pull():
    cmd("git pull origin master")

def __missing__(name):
    return "Command {} does not exist".format(name)

def parse_arguments():

    ap = ArgumentParser()
    sub = ap.add_subparsers(title="Subcommands")
    
    # *******************
    # * Commit and push *
    # *******************
    
    sub_comp = sub.add_parser("compush", help="Commit and push changes.")
    
    sub_comp.add_argument(
        "message",
        type=str,
        help="Commit message.")
    
    sub_comp.set_defaults(func=compush)
    
    # *************
    # * Add files *
    # *************
    
    sub_add = sub.add_parser("add", help="Add files to repository.")
    
    sub_add.add_argument(
        "files",
        type=str,
        nargs="+",
        help="List of files to add.")

    sub_add.set_defaults(func=add)
    
    # ******************************
    # * Pull files from repository *
    # ******************************
    
    sub_pull = sub.add_parser("pull", help="Pull changes from repository.")
    sub_pull.set_defaults(func=pull)
    
    return ap.parse_args()


main = __import__(__name__)

if __name__ == "__main__":
    pl.call(main)
