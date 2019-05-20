#!/usr/bin/env python

from subprocess import Popen, PIPE, check_output
from shlex import split
from os.path import join as pjoin, basename
from glob import iglob
from argparse import ArgumentParser
from tempfile import _get_default_tempdir


opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

home = "/home/istvan"
progs = pjoin(home, "progs")
temu = "lxterminal"
gamma_doc = pjoin(home, "Dokumentumok", "gamma_doc")


class dmenu(object):
    cmd = "dmenu %s" % opt
    
    def __init__(self, *args, **kwargs):
        self.msg = kwargs.pop("msg", None)
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
        cmd = dmenu.cmd
        
        if self.msg is not None:
            cmd += ' -p "%s"' % self.msg
        
        p = Popen(split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
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
            cmd = '%s "%s"' % (self.cmd, mode)
        
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


_modules = {
    "mc": dmenu(home, **repos, cmd="mc", interm=True, msg="Select directory!"),
    
    "playlists": dmenu.file_list(home, "Zenék", "playlists", "*", cmd="parole",
                                 msg="Select playlist!"),
    
    "gamma_doc": dmenu.file_list(home, gamma_doc, "*.html", msg="Select doc!",
                                          cmd="chromium-browser"),
    "pull_all": pull_all,
    "eofs": eofs,
}


def main():
    
    ap = ArgumentParser()
    
    ap.add_argument("mode", help="Mode", type=str,
                    choices=["modules", "programs", "pull_all", "markdown"])
    
    ap.add_argument("--infile", help="Infile", type=str, nargs="?")
    
    args = ap.parse_args()
    
    
    if args.mode == "modules":
        modules(**_modules)
    
    elif args.mode == "pull_all":
        pull_all()
        
    elif args.mode == "markdown":
        # User-defined mode. The nine following command-line arguments are
        # taken to be respectively the macro start sequence, the macro end
        # sequence for a call without arguments, the argument start sequence,
        # the argument separator, the argument end sequence, the list of
        # characters to stack for argument balancing, the list of characters
        # to unstack, the string to be used for referring to an argument by
        # number, and finally the quote character (if there is none an
        # empty string should be provided).
        
        # macro start, macro end, arg start, arg sep, arg end,
        # char list to stack, char list to unstack, arg ref by num, quote char
        
        # opts = '-U "\\\\" "" "{" "," "}" "{" "}" "#" "@"'
        udef = {
            "macro_start": "@",
            "macro_end": r"",
            "arg_start": "(",
            "arg_end": ")",
            "arg_sep": ",",
            "stack": "(",
            "unstack": ")",
            "bynum": "#",
            "quote": ""
        }
        
        mdef = {
            "macro_start": r"\n#\w",
            "macro_end": r"\n",
            "arg_start": " ",
            "arg_end": r"\n",
            "arg_sep": " ",
            "stack": "",
            "unstack": "",
        }
        
        opts = (
            '-U "{macro_start}" "{macro_end}" "{arg_start}" "{arg_sep}" '
            '"{arg_end}" "{stack}" "{unstack}" "{bynum}" "{quote}" '
        ).format(**udef)
        
        
        if 1:
            opts += (
                '-M "{macro_start}" "{macro_end}" "{arg_start}" "{arg_sep}" '
                '"{arg_end}" "{stack}" "{unstack}"'
            ).format(**mdef)
        
        
        cmd = 'gpp %s -n --nostdinc +c "/*" "*/" +c "%%" "\\n" %s -o %s' \
              % (opts, args.infile, md_temp)
        
        
        # print(cmd)
        
        check_output(split(cmd))
        
    else:
        check_output(split("dmenu_run %s" % opt))
    
        
    return 0


if __name__ == "__main__":
    main()