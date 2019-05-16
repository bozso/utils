PROGS="/home/istvan/progs"
UTILS_DIR="$PROGS/utils"


alias reload='source $UTILS_DIR/utils.sh'

export temu=lxterminal
browser="chromium-browser"

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
            push $1
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

proton() {
    check_narg $# 1
    
    local p_sapps="/home/istvan/.steam/steam/steamapps"
    local p_compat="$p_sapps/compatdata/eofs"
    local e_proton="$p_sapps/common/Proton 3.16/proton"
    local p_freetype="/usr/lib/x86_64-linux-gnu/libfreetype.so.6"
    
    # STEAM_COMPAT_DATA_PATH="/home/istvan/.proton/" python "$e_proton" run $1 LD_PRELOAD=$p_freetype 
    # PROTON_USE_WINED3D11=1 \
    # PROTON_NO_ESYNC=1 \
    STEAM_COMPAT_DATA_PATH=$p_compat \
    DXVK_LOG_LEVEL=debug \
    python "$e_proton" run $1
    
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

alias editor="$PROGS/textadept/textadept"

ta() {
    editor -u "$TXA" "$@" &
}


markdown_compile() {
    local tmp="/tmp/tmp.md"

    cpp -nostdinc -x c $1 -P > $tmp
    $browser $tmp
}


alias nano="nano -u"
alias nbrc="nano -u ~/.bashrc"
alias pull_all="$UTILS_DIR/utils.py pull_all"


. "$PROGS/insar_meteo/insar_meteo.sh"


JULIA="$PROGS/julia-1.1.0/bin"
SNAP="/home/istvan/snap/bin"
SSARA="$PROGS/SSARA"
GAMMA="$PROGS/gamma"


PATH="$PATH:$JULIA:$SNAP:$SSARA:$PROGS/bin:$PROOT/usr/bin:$UTILS_DIR/bin"

export LD_LIBRARY_PATH="LD_LIBRARY_PATH:$PROOT/usr/lib/x86_64-linux-gnu"
export PYTHONPATH="$PYTHONPATH:$UTILS_DIR:$GAMMA"
export CDPATH=".:~:~/progs:/mnt/bozso_i"

export OMP_NUM_THREADS=8

