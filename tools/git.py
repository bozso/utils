from os.path import join as pjoin

from tools import *

git_exe = "git"

def git(mode, cmd_args, *args):
    if cmd_args.path is not None:
        opts = '--git-dir="%s"' % (args.path)
    else:
        opts = ""
    
    out = cmd(git_exe, opts, mode, *args)
    
    print(out.decode())


def stat(args):
    git("status", args)


def push(args):
    git("commit", args, '-am "%s"' % args.message)
    git("push", args)

    
if __name__ == "__main__":
    ap = Argp(
        opt("path", help="Path to repository."),
        opt("user", help="Username"), subcmd=1
    )

    ap.subcmd(stat, help="Print status of git repository.")
    
    ap.subcmd(push,
        pos("message", type=str, help="Commit message.", nargs="+"),
    help="Commit and push changes.")
    
    
    args = ap.parse_args()
    args.fun(args)