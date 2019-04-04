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
        echoerr "error: gradd: One argument (remote repository address) is required!"
        return 1
    fi

    git remote add origin $1
}


function gs_pull {
    git pull origin master
}


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


PATH="$PATH:$JULIA:$SNAP:$SSARA:$PROGS:$PROOT/usr/bin:$UTILS_DIR/bin"

export LD_LIBRARY_PATH="LD_LIBRARY_PATH:$PROOT/usr/lib/x86_64-linux-gnu"
export PYTHONPATH="$PYTHONPATH:$UTILS_DIR"

export OMP_NUM_THREADS=8
