#! /usr/bin/env python

from argparse import ArgumentParser
from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split
import plac_core as pl

commands = "compush", "add", "pull", "status"

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

@pl.annotations(message=("Commit message."))
def compush(message):
    cmd("git commit -am \"{}\"".format(message))
    cmd("git push origin master")

@pl.annotations(files=("List of files to add."))
def add(files):
    if isinstance(files, str):
        cmd("git add {}".format(files))
    else:
        cmd("git add {}".format(" ".join(files)))
        
def pull():
    cmd("git pull origin master")

def status():
    print(cmd("git status").decode())

def __missing__(name):
    return "Command {} does not exist".format(name)

main = __import__(__name__)

if __name__ == "__main__":
    pl.call(main)
