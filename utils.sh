PROGS="${HOME}/progs"
UTILS="${PROGS}/utils"

alias reload='. ${UTILS}/utils.sh'
alias mods='sh ${UTILS}/menu.sh modules'

export temu=lxterminal
browser="chromium-browser"

for file in $(ls ${UTILS}/bash_completion/); do
    if [ -r ${file} ]; then
        . ${file}
    fi
done

buildpdf() {
    pdflatex --file-line-error-style -shell-escape "$1"
    bibtex "$(basename $1).aux"
    pdflatex --file-line-error-style -shell-escape "$1"
    pdflatex --file-line-error-style -shell-escape "$1"
}


local_install() {
    if [ "$#" != "1" ]; then
        printf "error: local_install: One argument (package name) is required!\n" >&2
        return 1
    fi
    
    rm *.deb
    
    apt download $1
    mkdir -p $PROOT

    dpkg -x *.deb $PROOT
    
    rm *.deb
}

tar_com() {
    tar -czvf $1.tar.gz $1
}

tar_ext() {
    tar -xzvf $1.tar.gz $1
}


gm() {
    sh ${UTILS}/tools/git.sh $*
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

alias nano="nano -u"
alias nbrc="nano -u ~/.bashrc"

PROOT="/home/istvan/packages"
PKGS="${HOME}/packages"


paths=\
"
${PROGS}/gamma
${PROGS}/stm-bi
${PROGS}/insar_meteo
"

for path in ${paths}; do
    p="${path}/init.sh"
    if [ -f "${p}" ]; then
        source "${p}" "${path}"
    fi
done

export PATH="${PATH}:$PROOT/usr/bin:${HOME}/.nimble/bin:${HOME}/go/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${PROOT}/usr/lib/x86_64-linux-gnu"
export PYTHONPATH="${PYTHONPATH}:${UTILS}"

export OMP_NUM_THREADS=8

