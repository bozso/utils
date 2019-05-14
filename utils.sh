PROGS="/home/istvan/progs"
UTILS_DIR="$PROGS/utils"


alias reload='source $UTILS_DIR/utils.sh'


update_clean() {
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    
    sudo apt-get clean
    sudo apt-get autoremove
}



buildpdf() {
    pdflatex --file-line-error-style -shell-escape "$1"
    bibtex "$(basename $1).aux"
    pdflatex --file-line-error-style -shell-escape "$1"
    pdflatex --file-line-error-style -shell-escape "$1"
}


tar_com() {
    tar -czvf $1.tar.gz $1
}

tar_ext() {
    tar -xzvf $1.tar.gz $1
}


perr() {
    printf "%s\n" "$*" >&2;
}


check_narg() {
    if [ "$1" -lt "$2" ]; then
        perr "error: Wrong number of arguments!"
        exit
    fi
}


push() {
    check_narg $# 1
    
    git commit -am $1
    git push origin master
}


pull() {
    git pull origin master

}

stat() {
    git status
}


gm() {
    check_narg $# 1
    
    case $1 in
        "push")
            push $2
            ;;
        "pull")
            pull
            ;;
        "stat")
            stat
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            exit
            ;;
    esac
}

#function gs_radd {
#
#    if [[ $# -ne 1 ]]; then
#        echoerr "error: gs_radd: One argument (remote repository address) is required!"
#        return 1
#    fi
#
#    git remote add origin $1
#}


PROOT="/home/istvan/packages"

#local_install() {
#    if [[ $# -ne 1 ]]; then
#        echoerr "error: local_install: One argument (package name) is required!"
#        return 1
#    fi
#    
#    rm *.deb
#    
#    apt download $1
#    mkdir -p $PROOT
#
#    dpkg -x *.deb $PROOT
#    
#    rm *.deb
#}


TXA="$UTILS_DIR/.textadept"

alias editor="$PROGS/textadept_10.4.x86_64/textadept"

ta() {
    editor -u "$TXA" "$@" &
}

alias nano="nano -u"
alias nbrc="nano -u ~/.bashrc"

. "$PROGS/insar_meteo/insar_meteo.sh"


JULIA="$PROGS/julia-1.1.0/bin"
SNAP="/home/istvan/snap/bin"
SSARA="$PROGS/SSARA"
GAMMA="$PROGS/gamma"


PATH="$PATH:$JULIA:$SNAP:$SSARA:$PROGS:$PROOT/usr/bin:$UTILS_DIR/bin"

export LD_LIBRARY_PATH="LD_LIBRARY_PATH:$PROOT/usr/lib/x86_64-linux-gnu"
export PYTHONPATH="$PYTHONPATH:$UTILS_DIR:$GAMMA"
export CDPATH=".:~:~/progs:/mnt/bozso_i"

export temu=lxterminal

export OMP_NUM_THREADS=8
