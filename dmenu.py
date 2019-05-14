#!/usr/bin/env python

from subprocess import Popen, PIPE, check_output
from shlex import split
from os.path import join as pjoin, basename
from glob import iglob

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
    
    
    def run(self):
        mode = self.select()
        
        if self.cmd is None:
            raise RuntimeError("cmd not defined!")
        
        if self.interm:
            cmd = "%s -e '%s %s'" % (temu, self.cmd, mode)
        else:
            cmd = "%s %s &" % (self.cmd, mode)
        
        print(cmd)
        
        check_output(split(cmd))
    

def paths(**kwargs):
    path = kwargs.pop("path")
    
    return {
        key: pjoin(path, key) if value is None else value
        for key, value in kwargs.items()
    }



def modules(**kwargs):
    
    module = dmenu(*kwargs.keys()).select()
    
    kwargs[module].run()
    
    
repos = paths(path=progs,
              insar_meteo=None,
              utils=None,
              texfile=pjoin(home, "Dokumentumok", "texfiles")
              )

        
def main():
    
    modules(mc=dmenu.file_list(home, "progs", "*", cmd="mc", interm=True),
            playlist=dmenu.file_list(home, "playlists", "*", cmd="parole"))
    
    return 0
    


if __name__ == "__main__":
    main()