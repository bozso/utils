#! /usr/bin/env sh

. "/home/istvan/progs/utils/utils.sh"

opt="-fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"

alias mymenu="dmenu $opt"


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
    while read data; do
        printf "%s\n" $(printf "%s\n" $data | awk -F '/' '{print $NF}')
    done
}


playlists() {
    local path="/home/istvan/playlists"
    
    local select=$(ls -1 $path/*.m3u | last_field | mymenu)
    
    if_nempty $select "parole $path/$select &"
}


mc() {
    local path="/home/istvan/progs"
    
    local select=$(ls -1 -d $path/* | last_field | \
                   mymenu -p "Select progs directory")
    if_nempty $select "$temu -e 'mc $path/$select'"
}


ssh() {
    local select=$(printf "robosztus\nzafir\n" | mymenu -p "Select server")
    
    case $select in
        "robosztus")
            $temu -e 'ssh -Y istvan@robosztus.ggki.hu'
            ;;
        "zafir")
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


select_module() {
    local select=$(printf "playlist\nmc\nssh\npush\npull" | mymenu -p "Select from modules")
    
    case $select in
        "playlist")
            playlists
            ;;
        "mc")
            mc
            ;;
        "ssh")
            ssh
            ;;
        "push")
            git_repo_manage push
            ;;
        "pull")
            git_repo_manage pull
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
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            exit 1
        ;;
    esac
}

main $@

