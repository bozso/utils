#!/usr/bin/env python

from subprocess import Popen, PIPE, check_output
from shlex import split
from os.path import join as pjoin, basename
from glob import iglob
from argparse import ArgumentParser

opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

home = "/home/istvan"
progs = pjoin(home, "progs")
temu = "lxterminal"


class dmenu(object):
    dmenu_cmd = split("dmenu %s" % opt)
    
    def __init__(self, *args, **kwargs):
        self.cmd, self.interm = kwargs.get("cmd"), kwargs.get("interm", False)
        
        
        self.options = {arg : arg for arg in args}
        
        _dict = kwargs.get("dict")
        if _dict is not None:
            self.options.update(_dict)
        
        self.choices = b"\n".join(choice.encode("ascii")
                                  for choice in self.options.keys())
    
    
    @classmethod
    def file_list(cls, *pattern, **kwargs):
        paths = {basename(path): path for path in iglob(pjoin(*pattern))}
        
        return cls(dict=paths, **kwargs)
    
    
    def select(self):
        p = Popen(dmenu.dmenu_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate(self.choices)
        
        if p.returncode != 0:
            raise RuntimeError("Non zero returncode from dmenu!")
        
        return self.options[out.decode().strip()]
    
    
    def __call__(self):
        mode = self.select()
        
        if self.cmd is None:
            raise RuntimeError("cmd not defined!")
        
        if self.interm:
            cmd = "%s -e '%s %s'" % (temu, self.cmd, mode)
        else:
            cmd = "%s %s &" % (self.cmd, mode)
        
        check_output(split(cmd))
        

def paths(**kwargs):
    path = kwargs.pop("path")
    
    return {
        key: pjoin(path, key) if value is None else value
        for key, value in kwargs.items()
    }



def modules(**kwargs):
    
    module = dmenu(*kwargs.keys()).select()
    
    kwargs[module]()
    
    
repos = paths(path=progs,
              insar_meteo=None,
              utils=None,
              texfile=pjoin(home, "Dokumentumok", "texfiles")
              )


def pull_repo(path):
    cmd = "git --git-dir=%s --work-tree=%s pull origin master" \
           % (pjoin(path, ".git"), path)
    
    check_output(split(cmd))



def pull_all():
    for repo in repos.values():
        pull_repo(repo)



def main():
    
    ap = ArgumentParser()
    
    ap.add_argument("mode", help="Mode", type=str,
                    choices=["modules", "programs"])
    
    args = ap.parse_args()
    
    if args.mode == "modules":
        modules(mc=dmenu.file_list(home, "progs", "*", cmd="mc", interm=True),
                playlist=dmenu.file_list(home, "playlists", "*", cmd="parole"),
                pull_all=pull_all)
    else:
        check_output(split("dmenu_run %s" % opt))
        
        
    return 0
    


if __name__ == "__main__":
    main()