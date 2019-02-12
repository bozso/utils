#! /usr/bin/env python

from utils import cmd, argp, narg

def compush(args):
    cmd("git commit -am \"{}\"".format(args.message))
    cmd("git push origin master")

def radd(args):
    cmd("git remote add origin {}".format(args.remote))
        
def pull():
    cmd("git pull origin master")

def main():

    ap = argp()
    ap.subp(title="subcommands")
    
    ap.subcmd("compush", compush,
        narg("message", help="Commit message.")
    )

    ap.subcmd("radd", radd,
        narg("remote", help="Remote repository to add.")
    )
    
    ap.subcmd("pull", pull)
    
    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
