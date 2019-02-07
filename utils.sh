#! /usr/bin/env sh

MAIN_DIR="/home/istvan/progs/utils"

export PATH="$PATH:$MAIN_DIR/bin"
export PYTHONPATH="$PYTHONPATH:$MAIN_DIR"

export CDPATH=.:~:~/progs:/mnt/bozso_i

alias sbrc='source ~/.bashrc'
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
