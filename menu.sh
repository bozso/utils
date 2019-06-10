#! /usr/bin/env sh

progs="$HOME/progs"
icons="$progs/utils/icons"

set -e

opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

alias mymenu="dmenu $opt -i"
alias dpass="dmenu $opt -nf \"black\" -nb \"black\" <&-"

temu="lxterminal"

debug() {
    notify-send -i "$icons/debug.png" "Debug" "$1" -t 2500
}

perr() {
    printf "%s\n" "$*" >&2;
}


check_narg() {
    if [ "$1" -lt "$2" ]; then
        perr "error: Wrong number of arguments!"
        return 1
    fi
}


dprompt() {
    [ "$(printf 'No\nYes' | mymenu -p "$1")" = "Yes" ] && $2
}


repos="
insar_meteo:$progs/insar_meteo\n
utils:$progs/utils\n
texfiles:/home/istvan/Dokumentumok/texfiles
"

key() {
    printf "%s\n" | awk -F ':' '{print $NF}' 
}

value() {
    printf "%s\n" | awk -F ':' '{print $1}' 
}

get_name() {
    awk -F ':' '{print $1}'
}

get_path() {
    awk -F ':' '{print $NF}'
}


get_pair() {
    for line in $repos; do
        case $(echo $line | get_name) in
            *$1*)
                echo $(echo $line | get_path)
                ;;
        esac
    done
}


repo_names=$(echo $repos | get_name)


notify() {
    if [ -n "$3" ]; then
        notify-send -i "$icons/$3" "$1" "$2" -t 1500
    else
        notify-send "$1" "$2" -t 1500
    fi
}


pull_all() {
    local tpl="https://bozso:%s@github.com/bozso"
    pwd="$(dpass -p "GitHub password:")"
    
    local tpl=$(printf "$tpl" $pwd)
    
    for line in $repos; do
        local name=$(echo $line | get_name)
        local path=$(echo $line | get_path)
        # cd
        # notify  "$path" "github.png"
        
        [ ! -d "$path"  ] && continue
        
        cd $path
        local curr="$tpl/$name"
        
        out=$(git pull $curr)

        notify "Pulling repo $name." "$out" "github.png"
    done

}


extract_music() {
    for zipfile in /tmp/*.zip; do
        local outpath="/home/istvan/Zenék/$(basename "$zipfile" .zip)"
        mkdir -p "$outpath"
        notify "Extracting file" "$zipfile"
        
        unzip "$zipfile" -d "$outpath"
    done
}


update_clean() {
    notify "Updating..."
    
    local o1=$(sudo apt-get update)
    local o2=$(sudo apt-get upgrade)
    local o3=$(sudo apt-get dist-update)
    
    # notify "Update complete." "$o1\n$o2\n$3"
    
    local o1="$(sudo apt-get clean)"
    local o2="$(sudo apt-get autoremove)"
    
    notify "Cleaning..."
    notify "Cleaning  complete." "$o1\n$o2"
}


last_field() {
    awk -F '/' '{print $NF}'
}


playlists() {
    local path="/home/istvan/Zenék/playlists"
    
    local sel=$(ls -1 $path/* | last_field | \
                mymenu -p "Select music:")
    
    if [ -n "$sel" ]; then
        local path="$path/$sel"
        notify "Playing music" "$path" "music_note.png"
        parole $path &
    fi
}


workspace() {
    check_narg $# "2"
    
    local name="$1"
    local path="$2"
    
    tmux start-server
    
    tmux new-session -d -t "$name"
    tmux send-keys "cd $path" C-m
    tmux split-window -h -c "$path"
    tmux select-pane -t 2
    tmux send-keys "mc" C-m
    tmux split-window -v -c "$path"
    tmux select-pane -t 1
    $temu -e "tmux attach-session -d -t \"$name\""

}

work() {
    local sel=$(printf "%s\n" $repo_names | mymenu -p "Select repo:")
    local path=$(get_pair $sel)
    
    workspace "$sel" "$path"
}


mc() {
    local sel="$(ls -d -1 $HOME/*/ | \
                 awk -F '/' '{print $(NF - 1)}' | \
                 mymenu -p "Select directory:")"
    
    if [ -n "$sel" ]; then
        local path="$HOME/$sel"
        notify "Started Midnight Commander." "$path" "mc.png"
        $temu -e "mc $path"
    fi
}


ssh() {
    local select=$(printf "robosztus\nzafir\n" | mymenu -p "Select server")
    
    local header="Connecting to remote machine."
    
    case $select in
        "robosztus")
            notify "$header" "istvan@robosztus.ggki.hu" "ssh.png"
            $temu -e 'ssh -Y istvan@robosztus.ggki.hu'
            ;;
        "zafir")
            notify "$header" "istvan@zafir.ggki.hu" "ssh.png"
            $temu -e 'ssh -Y istvan@zafir.ggki.hu'
            ;;
        *)
            printf "Unknown option: %s!\n" $select
    esac
}


md_tmp="/tmp/tmp.md"


markdown() {
    check_narg $# 1
    notify "Preprocessing markdown." "$1" "markdown.png"
    gpp -C --nostdinc $1 -o $md_tmp
}


git_remote_add() {
    check_narg $# 1

    git remote add origin "$1"
}


git_push() {
    check_narg $# 1

    git commit -am "$*"
    git push origin master
}


git_manage() {
    check_narg $# 1
    
    case $1 in
        "stat")
            git status
            ;;
        "push")
            shift
            git_push "$@"
            ;;
        "pull")
            git pull origin master
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
            ;;
    esac
}


shutdown_now() {
    dprompt "Did you push all git repositories?" ""
    dprompt "Shutdown?" "shutdown -h now"
}            


modules="
playlists
mc
ssh
pull_all
extract_music
work
"


select_module() {
    local sel=$(printf "%s\n" $modules | mymenu -p "Select from modules:")
    
    for module in $(printf "%s\n" $modules); do
        case $sel in
            $module)
                $module
                ;;
            *)
                ;;
        esac
    done
}


main() {
    check_narg $# 1
        
    case $1 in
        "programs")
            dmenu_run $opt
            ;;
        "modules")
            select_module
            ;;
        "markdown")
            markdown $2
            ;;
        "git")
            shift
            git_manage $@
            ;;
        "shutdown")
            shutdown_now
            ;;
        "pull_all")
            pull_all
            ;;
        "extract_music")
            extract_music
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
            ;;
    esac
}

main $@

