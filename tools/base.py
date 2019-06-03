from subprocess import check_output, STDOUT, CalledProcessError
from shlex import split
from os.path import join as pjoin, basename, splitext
from glob import iglob
from argparse import ArgumentParser
from tempfile import _get_default_tempdir


__all__ = [
    "cmd",
    "dmenu",
    "Repo",
    "Argp",
    "pos",
    "opt",
    "flag"
]

    
    
dopt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

home = "/home/istvan"
progs = pjoin(home, "progs")
temu = "lxterminal"
gamma_doc = pjoin(home, "Dokumentumok", "gamma_doc")


def cmd(*args, **kwargs):
    debug = kwargs.pop("debug", False)
    
    Cmd = " ".join(args)
    
    if debug:
        print(Cmd)
        return
    
    try:
        proc = check_output(split(Cmd), stderr=STDOUT)
    except CalledProcessError as e:
        print("\nNon zero returncode from command: \n'{}'\n"
              "\nOUTPUT OF THE COMMAND: \n\n{}\nRETURNCODE was: {}"
              .format(Cmd, e.output.decode(), e.returncode))
        raise e
    

    return proc

def pos(name, help=None, type=str, choices=None, nargs=None):
    return (name, help, None, "pos", None, type, choices, nargs)


def opt(name, help=None, alt=None, type=str, choices=None,
        default=None, nargs=None):
    return (name, help, default, "opt", alt, type, choices, nargs)
    

def flag(name, help=None, alt=None):
    return (name, help, None, "flag", alt, None, None, nargs)


class Argp(ArgumentParser):
    def __init__(self, *args, **kwargs):
        subcmd = bool(kwargs.pop("subcmd", False))
        
        ArgumentParser.__init__(self, **kwargs)
        
        if subcmd:
            self.subparser = self.add_subparsers(**kwargs)
        else:
            self.subparser = None
        
        self.addargs(*args)

    
    def addargs(self, *args):
        for arg in args:
            Argp.ap_add_arg(self, arg)

    
    def subp(self, **kwargs):
        if self.subparser is None:
            self.subparser = self.add_subparsers(**kwargs)
    
    
    def subcmd(self, fun, *args, **kwargs):
        subtmp = self.subparser.add_parser(fun.__name__, **kwargs)
        
        for arg in args:
            Argp.ap_add_arg(subtmp,  arg)
        
        subtmp.set_defaults(fun=fun)
    
    
    @staticmethod
    def ap_add_arg(obj, arg):
        if arg[3] == "opt":
            if arg[4] is not None:
                obj.add_argument(
                    "--{}".format(arg[0]), "-{}".format(arg[4]),
                    help=arg[1],
                    type=arg[5],
                    default=arg[2],
                    nargs=arg[7],
                    choices=arg[6])
            else:
                obj.add_argument(
                    "--{}".format(arg[0]),
                    help=arg[1],
                    type=arg[5],
                    default=arg[2],
                    nargs=arg[7],
                    choices=arg[6])
        elif arg[3] == "pos":
            obj.add_argument(
                arg[0],
                help=arg[1],
                type=arg[5],
                choices=arg[6])
        
        elif arg[3] == "flag":
            obj.add_argument(
                "--{}".format(arg[0]),
                help=arg[1],
                action="store_true")


class Repo(object):
    git_exe = "git"
    
    def __init__(self, path=".", github=False, user=None):
        self.path = pjoin(path, ".git")
        self.options = '--git-dir="%s"' % (self.path)
    
    def __call__(self, *args, **kwargs):
        cmd(Repo.git_exe, *args, **kwargs)
    
    def stat(self):
        self("status")

    def push(self):
        self("push")
    
    
class dmenu(object):
    cmd = "dmenu %s" % dopt
    
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


temp = pjoin(_get_default_tempdir(), "tmp%s")


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
                    choices=["modules", "programs", "pull_all", "markup"])
    
    ap.add_argument("--infile", help="Infile", type=str, nargs="?")
    
    args = ap.parse_args()
    
    
    if args.mode == "modules":
        modules(**_modules)
    
    elif args.mode == "pull_all":
        pull_all()
        
    elif args.mode == "markup":
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
        
        infile = args.infile
        
        ext = splitext(infile)[1]
        
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
        
        
        if 0:
            opts = (
                '-U "{macro_start}" "{macro_end}" "{arg_start}" "{arg_sep}" '
                '"{arg_end}" "{stack}" "{unstack}" "{bynum}" "{quote}" '
            ).format(**udef)
        
        
        if 0:
            opts += (
                '-M "{macro_start}" "{macro_end}" "{arg_start}" "{arg_sep}" '
                '"{arg_end}" "{stack}" "{unstack}"'
            ).format(**mdef)
        
        
        opts = '-T +c "/*" "*/" --nostdinc'
        
        cmd = "gpp %s %s -o %s" % (opts, infile, temp % ".md")
        
        check_output(split(cmd))
        
    else:
        check_output(split("dmenu_run %s" % opt))
    
        
    return 0


if __name__ == "__main__":
    main()