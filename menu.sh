#! /usr/bin/env sh

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


if_nempty() {
    if [ -n "$1" ]; then
        eval "$2"
    fi
}


last_field() {
    awk -F '/' '{print $NF}'
}


playlists() {
    local path="/home/istvan/Zenék/playlists"
    
    local select=$(ls -1 $path/* | last_field | mymenu)
    
    if_nempty $select "parole $path/$select &"
}


notify() {
    if [ -n "$3" ]; then
        notify-send -i "$ICONS/$3" "$1" "$2"
    else
        notify-send "$1" "$2"
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
    
    case $select in
        "robosztus")
            notify-send "Connecting to remote machine:" "istvan@robosztus.ggki.hu"
            $temu -e 'ssh -Y istvan@robosztus.ggki.hu'
            ;;
        "zafir")
            notify-send "Connecting to remote machine:" "istvan@zafir.ggki.hu"
            $temu -e 'ssh -Y istvan@zafir.ggki.hu'
            ;;
        *)
            printf "Unknown option: %s!\n" $select
    esac
}


git_repo_manage() {
    local path="/home/istvan/progs"
    local gtmp="/tmp/git_commit_tpl"
    
    
    
    
    
    local select=$(printf "utils\ngamma\ninsar_meteo\n"| mymenu -p "Select from github repos")
    
    local gdir=$(printf "--git-dir=%s/%s" $path $select)
    local _push="nano \"$gtmp\";git commit -a -F \"$gtmp\" $gdir;\
                 git push origin master $gdir;rm \"$gtmp\";"
    
    case $1 in
        "pull")
            $temu -e "echo asd; cd $path/$select; git pull origin master"
            ;;
        "push")
            # $temu -e sh -c "$_push"
            # ta "$gtmp"
            $temu -e "git commit -a $gdir > /home/istvan/debug"

            #cd $path/$select
            #
            #echo "Set commit message"
            #nano "$gtmp"
            #
            #git commit -a -F "$gtmp"
            #git push origin master
            #
            #rm "$gtmp"
            ;;
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


main() {
    check_narg $# 1
    #local select=$(printf "%s\n" $repo_names | \
    #               mymenu -p "Select progs directory")
    #
    #echo $select
    #
    #return
    
    # get_pair "insar_meteo"
    
    #return
    
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
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            exit
        ;;
    esac
}

main $@

