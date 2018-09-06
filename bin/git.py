#! /usr/bin/env python

from utils import cmd
import plac_core as pl

commands = "compush", "add", "pull", "radd"


@pl.annotations(message=("Commit message.", "positional", None, str))
def compush(message):
    cmd("git commit -am \"{}\"".format(message))
    cmd("git push origin master")

@pl.annotations(files=("List of files to add.", "positional", None, str))
def add(files):
    if isinstance(files, str):
        cmd("git add {}".format(files))
    else:
        cmd("git add {}".format(" ".join(files)))

@pl.annotations(remote=("Remote repository to add.", "positional", None, str))
def radd(remote):
    cmd("git remote add origin {}".format(remote))
        
def pull():
    cmd("git pull origin master")

def __missing__(name):
    return "Command {} does not exist".format(name)

main = __import__(__name__)

if __name__ == "__main__":
    pl.call(main)
