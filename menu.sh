#! /usr/bin/env sh

set -e

. "/home/istvan/progs/utils/utils.sh"

ICONS="$UTILS_DIR/icons"

opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

alias mymenu="dmenu $opt"


repos="
insar_meteo:$PROGS/insar_meteo\n
utils:$PROGS/utils\n
texfiles:/home/istvan/Dokumentumok/texfiles
"

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
        notify-send -i "$ICONS/$3" "$1" "$2" -t 1500
    else
        notify-send "$1" "$2" -t 1500
    fi
}


_pull_all() {
    local tpl="https://bozso@github.com/bozso"
    for line in $repos; do
        local name=$(echo $line | get_name)
        local path=$(echo $line | get_path)
        # cd
        # notify  "$path" "github.png"
        
        pwd=$(dmenu -p "GitHub password:")
        
        cd $path
        
        local curr="$tpl/$name"
        out=$(git pull $curr)

        notify "Pulling repo: $name" "$out" "github.png"
    done
}


extract_music() {
    # IFS=$'\n'
    for zipfile in /tmp/*.zip; do
        local outpath="/home/istvan/Zenék/$(basename "$zipfile" .zip)"
        mkdir -p $outpath
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
    
    local select=$(ls -1 $path/* | last_field | mymenu)
    
    
    if [ -n "$select" ]; then
        local path="$path/$select"
        notify "Playing music" "$path" "music_note.png"
        parole $path &
    fi
}


commander() {
    local select=$(printf "%s\n" $repo_names | \
                   mymenu -p "Select progs directory:")
    
    if [ -n "$select" ]; then
        local path=$(get_pair $select)
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


modules="
playlist
mc
ssh
pull_all
shutdown
extract_music
update_clean
"


select_module() {
    local select=$(printf "%s\n" $modules | mymenu -p "Select from modules:")
    
    case $select in
        "playlist")
            playlists
            ;;
        "mc")
            commander
            ;;
        "ssh")
            ssh
            ;;
        "pull_all")
            _pull_all
            ;;
        "extract_music")
            extract_music
            ;;
        "update_clean")
            update_clean
            ;;
        "shutdown")
            [ "$(printf 'Yes\nNo' | dmenu -p 'Shutdown?')" = "Yes" ] && \
            shutdown -h now
            ;;
    esac
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
        "pull_all")
            _pull_all
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

