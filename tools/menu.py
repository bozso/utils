#!/usr/bin/env python

from os.path import join
from glob import iglob, glob

from base import *
from manage import manage
from dmenu import progs, select
from sys import argv



md_inc_path = join(home, "Dokumentumok", "texfiles", "gpp")
md_path = "/tmp/tmp.md"
md_rules = \
'-U "@" "" "{" "}{" "}" "{" "}" "@" "" ' \
'-M "#" "\n" "{" "}{" "}" "{" "}" ' \
'+c "/*" "*/" +c "//" "\n"'

def markdown():
    path = argv[2]
    # notify "Preprocessing markdown." "$1" "markdown.png"
    # 
    # gpp $1 --nostdinc -o $md_tmp -I${inc_path} \
    # -U "@" "" "{" "}{" "}" "{" "}" "@" "" \
    # -M "#" "\n" "{" "}{" "}" "{" "}" \
    # +c "/*" "*/" +c "//" "\n"
    notify(path, header="Preprocessing markdown", icon="markdown.png")
    
    cmd("gpp", path, "--nostdinc", "-o %s" % md_path,
        "-I%s" % md_inc_path, md_rules)


def playlists():
    # local path="/home/istvan/Zenék/playlists"
    # 
    # local sel=$(ls -1 $path/* | last_field | \
    #             mymenu -p "Select music:")
    # 
    # if isset $sel
    #     local path="$path/$sel"
    #     notify "Playing music" "$sel" "music_note.png"
    #     parole $path &
    
    path = join(home, "Zenék", "playlists")
    
    sel = select(*glob(join(path, "*")), prompt="Select music:")
    
    notify(sel, header="Playing music", icon="music_note.png")
    cmd("parole %s &" % join(path, sel))


def git():
    manage("git")


def mc():
    sel = select(*glob(join(home, "*")), prompt="Select directory:")
    
    notify(sel, header="Starting Midnight Commander", icon="mc.png")
    cmd(temu, "-e %s" % join(home, sel))
    
    # local sel="$(ls -d -1 $HOME/*/ | \
    #              awk -F '/' '{print $(NF - 1)}' | \
    #              mymenu -p "Select directory:")"
    # 
    # if isset $sel
    #     local path="$HOME/$sel"
    #     notify "Started Midnight Commander." "$path" "mc.png"
    #     $temu -e "mc $path"


def ssh():    
    sel = select("robosztus", "zafir", prompt="Select server")
    address = "istvan@%s.ggki.hu" % sel
    
    notify(address, header="Connecting to remote machine.", icon="ssh.png")
    cmd(temu, "ssh -Y  -e %s" % address)


def repos_all():
    pass


def extract_music():
    for zipfile in iglob("/tmp/*.zip"):
        outpath = join(home, "Zenék", basename(zipfile))
        notify(zipfile, header="Extracting file")
        
        # Unzip
        # unzip "$zipfile" -d "$outpath"


def workspace(name, path):
    # tmux start-server
    # 
    # echo "$name $(tmux ls)"
    # local bool="$(in_str "$name" "$(tmux ls)")"
    # echo "$bool"
    # 
    # if $bool is "false"
    #     notify "tmux" "Starting session $name"
    #     tmux new-session -d -t "$name"
    #     tmux send-keys "cd $path" C-m
    #     tmux split-window -h -c "$path"
    #     tmux select-pane -t 2
    #     tmux send-keys "mc" C-m
    #     tmux split-window -v -c "$path"
    #     tmux select-pane -t 1
    # 
    # $temu -e "tmux attach-session -d -t \"$name\""
    pass

def work():
    # local sel="$(dselect "$repos" "Select repo:")"
    # local path="$(mget "$sel" "$repos")"
    # 
    # workspace "$sel" "$path"
    pass


def select_module():
    sel = select(*modules.keys(), p="Select module:")
    modules[sel]()


modules = {
    "playlists" : playlists,
    "git" : git,
    "mc" : mc,
    "ssh" : ssh,
    "repos_all" : repos_all,
    "extract_music" : extract_music,
    "work" : work
}


mode = {
    "programs": progs,
    "modules": select_module,
    "markdown": markdown
}


def main():
    mode[argv[1]]()
    

if __name__ == "__main__":
    main()