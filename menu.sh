#! /usr/bin/env sh

progs="${HOME}/progs"
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


notify() {
    return
    if [ -n "$3" ]; then
        notify-send -i "$icons/$3" "$1" "$2" -t 1500
    else
        notify-send "$1" "$2" -t 1500
    fi
}


extract_music() {
    for zipfile in /tmp/*.zip; do
        local outpath="/home/istvan/Zenék/$(basename "$zipfile" .zip)"
        # mkdir -p "$outpath"
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
        notify "Playing music" "$sel" "music_note.png"
        parole $path &
    fi
}


workspace() {
    check_narg $# "2"
    
    local name="$1"
    local path="$2"
    
    tmux start-server
    
    echo "$name $(tmux ls)"
    local bool="$(in_str "$name" "$(tmux ls)")"
    echo "$bool"
    
    if [ "$bool" = "false" ]; then
        notify "tmux" "Starting session $name"
        tmux new-session -d -t "$name"
        tmux send-keys "cd $path" C-m
        tmux split-window -h -c "$path"
        tmux select-pane -t 2
        tmux send-keys "mc" C-m
        tmux split-window -v -c "$path"
        tmux select-pane -t 1
    fi
    
    $temu -e "tmux attach-session -d -t \"$name\""

}

work() {
    local sel="$(dselect "$repos" "Select repo:")"
    local path="$(mget "$sel" "$repos")"
    
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



servers="\
robosztus : robosztus.ggki.hu
zafir     : zafir.ggki.hu
eejit     : eejit.geo.uu.nl
"

manage_ssh() {
    local mode="$1"
    
    server=$(printf '%s\n' "${servers}" | \
             mymenu -p "Select server" -l 3)
    
    
    local addr="$(printf '%s' "${server}" \
                  | cut -d ':' -f 2 \
                  | tr -d ' ')"
    
    local addr="$(printf 'istvan@%s' "${addr}")"
    
    case "${mode}" in
        "mount")
            local name="$(printf '%s' "${server}" \
                          | cut -d ':' -f 1 \
                          | tr -d ' ')"
            
            local path="${HOME}/mount/${name}"
            local cmd="$(printf 'sshfs %s: %s' "${addr}" "${path}")"
            #local cmd="${temu} --command=\"${cmd}\""
            $cmd
            # >&2 "${HOME}/menu.log"
            ;;
        "join")
            local cmd="$(printf 'ssh -Y %s' "${addr}")"
            $cmd
            ;;
        *)
            printf 'Unknown option: %s!\n' "{mode}"
    esac
}

connect() {
    manage_ssh "join"
}

mount() {
    manage_ssh "mount"
}

shutdown_now() {
    notify-send "Did you push all git repositories?" \
    "Check git repositories!" -u "critical" -i "$icons/warning.png"
    dprompt "Shutdown?" "shutdown -h now"
}


gamma() {
    local path="/home/istvan/Dokumentumok/gamma_doc"
    
    local sel=$(ls -1 $path/*.html | last_field | \
                mymenu -p "Select program:" -l 10)
    
    if [ -n "$sel" ]; then
        local path="$path/$sel"
        notify "Opening documentation" "${sel}" "music_note.png"
        chromium-browser "${path}"
    fi
}

modules="
playlists
git
mc
connect
repos_all
extract_music
work
gamma
mount
"


select_module() {
    local log="$HOME/menu.log"
    local sel=$(printf "%s\n" ${modules} | mymenu -p "Select from modules:")
    
    for module in $(printf "%s\n" $modules); do
        case $sel in
            $module)
                #$module > $log
                $module
                ;;
            *)
                ;;
        esac
    done
}

Basename() {
    while IFS= read -r line; do
      printf '%s\n' "$(basename $line .png)"
    done    
}

import() {
    local root="${HOME}/screencap"
    mkdir -p "${root}"
    
    last="$(ls ${root}/img_*.png \
            | Basename \
            | tr -d '[:alpha:]' \
            | tr -d '_' \
            | sort -g \
            | tail -1)"
    
    new=$((last+1))
    
    import "${root}/img_${new}.png" > "${HOME}/import.log"
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
        "shutdown")
            shutdown_now
            ;;
        "import")
            import
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
            ;;
    esac
}

main "$@"
