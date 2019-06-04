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


extract_music() {
    IFS=$'\n'
    for zipfile in $(ls /tmp/*.zip); do
        outpath="/home/istvan/Zenék/$(basename $zipfile .zip)"
        mkdir $outpath
        unzip $zipfile -d $outpath
    done
}



last_field() {
    awk -F '/' '{print $NF}'
}


notify() {
    if [ -n "$3" ]; then
        notify-send -i "$ICONS/$3" "$1" "$2"
    else
        notify-send "$1" "$2"
    fi
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


modules="
playlist
mc
ssh
pull_all
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
            pull_all
            ;;
    esac
}


md_tmp="/tmp/tmp.md"


markdown() {
    check_narg $# 1
    gpp -C --nostdinc $1 -o $md_tmp
}


git_status() {
    git status
}

git_remote_add() {
    check_narg $# 1

    git remote add origin $1
}


git_push() {
    check_narg $# 1
    echo "git commit -a -m \"$@\""
    git commit -a -m "$@"
    git push origin master
}



git_manage() {
    check_narg $# 1
    
    case $1 in
        "stat")
            git_status
            ;;
        "push")
            shift
            git_push "$@"
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
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
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
            ;;
    esac
}

main $@

