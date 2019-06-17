#! /usr/bin/env python

from os import chdir
from os.path import exists
from sys import argv

from common import *
import tmux as tm
import dmenu as dm



git_bin = "git"


def git(*args, **kwargs):
    return cmd(git_bin, *args, **kwargs)


def main():
    tpl = "https://bozso:%s@github.com/bozso"
    
    assert argv[1] in ("git", "tmux")
    
    if argv[1] == "git":
        if len(argv) > 2 and argv[2] == "all":
            repo = "all"
            mode = dm.select("pull", "commit", "status",
                             p="Select action for all repositories:")
        else:
            repo = dm.select("all", p="Select a repository:", **repos)
            mode = dm.select("pull", "commit", "status", p="Select action:")
    
        if repo == "all":
            _repos = repos
        else:
            _repos = {repo: repos[repo]}
        
        
        if mode in ("pull", "commit"):
            pwd = dm.password(p="Github password:")
            tpl = tpl % pwd
        
        
        for name, path in _repos.items():
            if not exists(path):
                continue
            
            chdir(path)
            
            if mode == "pull":
                notify(git("pull", "%s/%s" % (tpl, name)),
                       header="Pulling repositroy %s." % name,
                       icon="github.png")
            
            elif mode == "commit":
                msg = din(p="Commit message:")
                git("commit", '-am "%s"' % msg)
                git("push", "%s/%s" % (tpl, name))
            
            elif mode == "status":
                notify(git("status"), header="Repository %s status." % name,
                       icon="github.png")
        
    elif argv[1] == "tmux":
        pass


if __name__ == "__main__":
    main()
