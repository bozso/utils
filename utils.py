#!/usr/bin/env python

from subprocess import Popen, PIPE, check_output
from shlex import split
from os.path import join as pjoin, basename
from glob import iglob
from argparse import ArgumentParser
from webbrowser import get
from tempfile import _get_default_tempdir
from utils.quik import Template


browser = get("chromium-browser")

opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

home = "/home/istvan"
progs = pjoin(home, "progs")
temu = "lxterminal"
gamma_doc = pjoin(home, "Dokumentumok", "gamma_doc")


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
            cmd = "%s %s" % (self.cmd, mode)
        
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
              gamma=None,
              insar_meteo=None,
              utils=None,
              texfile=pjoin(home, "Dokumentumok", "texfiles")
              )


def pull_repo(path):
    cmd = "git --git-dir=%s --work-tree=%s pull origin master" \
           % (pjoin(path, ".git"), path)
    
    try:
        with open(pjoin(home, "dmenu.py.log"), "ab") as f:
            f.write(check_output(split(cmd)))
    except:
        pass


def pull_all():
    for repo in repos.values():
        pull_repo(repo)


def eofs():
    path = pjoin(home, "progs", "eofs", "game")
    jar = pjoin(path, "Phoenix.jar")
    cmd = pjoin(path, "jre", "bin", "java")
    
    cmd += " -jar -Xss32m %s --enableai -d" % jar
    
    print(cmd)
    
    # check_output(split(cmd))

md_temp = pjoin(_get_default_tempdir(), "tmp.md")

def main():
    
    ap = ArgumentParser()
    
    ap.add_argument("mode", help="Mode", type=str,
                    choices=["modules", "programs", "pull_all", "markdown"])
    
    ap.add_argument("--infile", help="Infile", type=str, nargs="?")
    
    args = ap.parse_args()
    
    if args.mode == "modules":
        
        modules(mc=dmenu.file_list(home, "progs", "*", cmd="mc", interm=True),
                playlist=dmenu.file_list(home, "playlists", "*", cmd="parole"),
                gamma_doc=dmenu.file_list(home, gamma_doc, "*.html",
                                          cmd="chromium-browser"),
                pull_all=pull_all,
                eofs=eofs)
    
    elif args.mode == "pull_all":
        pull_all()
    elif args.mode == "markdown":
        with open(args.infile, "r") as f:
            tpl = Template(f.read())
        
        with open(md_temp, "w") as f:
            f.write(tpl.render({}))
        
        #run_fypp2([args.infile, md_temp])
        
        # cmd = "gpp -C --nostdinc %s -o %s +c /* */" % (, )
        # check_output(split(cmd))

    else:
        check_output(split("dmenu_run %s" % opt))
        
            
        
    return 0
    


if __name__ == "__main__":
    main()