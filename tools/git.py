from os.path import join as pjoin

from tools import *


class Repo(CParse):
    git_exe = "git"
    commands = ("stat", "push")
    
    @annot(
        path=opt(default=None, help="Path to git repository.", short="p")
    )
    def __init__(self, **kwargs):
        CParse.__init__(self, **kwargs)
        
        self.parse()
        
        path = self["path"]
        if path is not None:
            self.path = pjoin(path, ".git")
            self.options = '--git-dir="%s"' % (path)
        else:
            self.options = ""
    

    def __call__(self, *args, **kwargs):
        print(cmd(Repo.git_exe, self.options, *args, **kwargs).decode())
    
    
    def stat(self):
        self("status")
    
    @annot(
        message=pos(help="Commit message")
    )
    def push(self):
        self("commit", '-am "%s"' % self["message"])
        self("push")



def git(mode, cmd_args, *args):
    if cmd_args.path is not None:
        opts = '--git-dir="%s"' % (args.path)
    else:
        opts = ""
    
    out = cmd(git_exe, opts, mode, *args)
    
    print(out.decode())


def main():
    
    repo = Repo()
    repo.args.fun()
    
    return 0

if __name__ == "__main__":
    
    main()
    
    #ap = Argp(
    #    opt("path", help="Path to repository."),
    #    opt("user", help="Username"), subcmd=1
    #)
#
    #ap.subcmd(stat, help="Print status of git repository.")
    #
    #ap.subcmd(push,
    #    pos("message", type=str, help="Commit message.", nargs="+"),
    #help="Commit and push changes.")
    #
    #
    #args = ap.parse_args()
    #args.fun(args)