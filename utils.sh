#! /usr/bin/env sh

UTILS_DIR="/home/istvan/progs/utils"

export CDPATH=.:~:~/progs:/mnt/bozso_i

alias reload='source $UTILS_DIR/utils.sh'
alias gs_stat='git status'


function update_clean {
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    
    sudo apt-get clean
    sudo apt-get autoremove
}


function extract_music {
    IFS=$'\n'
    for zipfile in $(ls /tmp/*.zip); do
        outpath="/home/istvan/Zenék/$(basename $zipfile .zip)"
        mkdir $outpath
        unzip $zipfile -d $outpath
    done
}


function buildpdf {
    pdflatex --file-line-error-style -shell-escape "$1"
    bibtex "$(basename $1).aux"
    pdflatex --file-line-error-style -shell-escape "$1"
    pdflatex --file-line-error-style -shell-escape "$1"
}


function tar_com {
    tar -czvf $1.tar.gz $1
}

function tar_ext {
    tar -xzvf $1.tar.gz $1
}

function echoerr {
    printf "%s\n" "$*" >&2;
}


function gs_push {
    if [[ $# -ne 1 ]]; then
        echoerr "error: gpush: One argument (message) is required!"
        return 1
    fi
    
    git commit -am "$1"
    git push origin master
}


function gs_radd {

    if [[ $# -ne 1 ]]; then
        echoerr "error: gs_radd: One argument (remote repository address) is required!"
        return 1
    fi

    git remote add origin $1
}


function gs_pull {
    git pull origin master
}


# dmenu_options="-fn -adobe-helvetica-bold-r-normal-*-20-180-100-100-p-138-iso8859-1"
# -adobe-helvetica-bold-r-normal-*-20-180-100-100-p-138-iso8859-1

dmenu_options="-fn -adobe-helvetica-bold-r-normal-*-20-180-100-100-p-138-iso8859-1"

alias mdmenu="dmenu -fn -adobe-helvetica-bold-r-normal-*-20-180-100-100-p-138-iso8859-1"



function if_nempty {
    if [ -n "$1" ]; then
        eval "$2"
    fi
}


function last_field {
    while read data; do
        echo $(echo $data | awk -F '/' '{print $NF}')
    done
}


function dmenu_playlists {
    local path="/home/istvan/playlists"
    
    local select=$(ls -1 $path/*.m3u | last_field | mdmenu)
    
    if_nempty $select "parole $path/$select &"
}


function dmenu_mc {
    local path="/home/istvan/progs"
    
    local select=$(ls -1 -d $path/* | last_field | \
                   mdmenu -p "Select pros directory")
    if_nempty $select "xfce4-terminal -e 'mc $path/$select'"
}


function dmenu_ssh {
    local options="robosztus\nzafir\n"
    local select=$(echo -e "$options" | mdmenu -p "Select server")
    
    case $select in
        "robosztus")
            xfce4-terminal -e 'ssh -Y istvan@robosztus.ggki.hu'
            ;;
        "zafir")
            xfce4-terminal -e 'ssh -Y istvan@zafir.ggki.hu'
            ;;
        *)
            echo "Unknown option: $select."
    esac
}


function dmenu_git_repo_manage {
    local path="/home/istvan/progs"
    local options="utils\ngamma\ninsar_meteo\n"
    local gtmp="/tmp/git_commit_tpl"
    local select=$(echo -e "$options"| mdmenu -p "Select from github repos")
    
    case $1 in
        "pull")
            cd $path/$select
            git pull origin master
            ;;
        "push")
            cd $path/$select
            
            echo "Set commit message"
            nano "$gtmp"
            
            git commit -a -F "$gtmp"
            git push origin master
            
            rm "$gtmp"
            ;;
    esac
}


function select_dmenu_module {
    local options="playlist\nmc\nssh\npush\npull"
    local select=$(echo -e "$options"| mdmenu -p "Select from modules")
    
    case $select in
        "playlist")
            dmenu_playlists
            ;;
        "mc")
            dmenu_mc
            ;;
        "ssh")
            dmenu_ssh
            ;;
        "push")
            dmenu_git_repo_manage push
            ;;
        "pull")
            dmenu_git_repo_manage pull
            ;;
    esac
}


alias dmenu_programs="dmenu_run -fn -adobe-helvetica-bold-r-normal-*-25-180-100-100-p-138-iso8859-1"


PROOT="/home/istvan/packages"

function local_install {
    if [[ $# -ne 1 ]]; then
        echoerr "error: local_install: One argument (package name) is required!"
        return 1
    fi
    
    rm *.deb
    
    apt download $1
    mkdir -p $PROOT

    dpkg -x *.deb $PROOT
    
    rm *.deb
}


TXA="$UTILS_DIR/.textadept"


function ta {
    txa -u "$TXA" "$@" &
}


alias tgam="ta -s $TXA/gamma &"

alias attach="tmux attach -t"
alias nano="nano -u"
alias nbrc="nano -u ~/.bashrc"


PROGS="/home/istvan/progs"

source "$PROGS/insar_meteo/insar_meteo.sh"


JULIA="$PROGS/julia-1.1.0/bin"
SNAP="/home/istvan/snap/bin"
SSARA="$PROGS/SSARA"
GAMMA="$PROGS/gamma"


PATH="$PATH:$JULIA:$SNAP:$SSARA:$PROGS:$PROOT/usr/bin:$UTILS_DIR/bin"

export LD_LIBRARY_PATH="LD_LIBRARY_PATH:$PROOT/usr/lib/x86_64-linux-gnu"
export PYTHONPATH="$PYTHONPATH:$UTILS_DIR:$GAMMA"

export OMP_NUM_THREADS=8
