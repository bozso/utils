#! /usr/bin/env sh

progs="${HOME}/progs"


start_tpl="
=============
*
* Repository: %s
*
"

end_tpl="
*
* End repository: %s
*
"

repos="
${progs}/insar_meteo
${progs}/utils
${progs}/gamma
${progs}/geodynamics
${HOME}/Dokumentumok/texfiles
"


check_narg() {
    if [ "$1" -lt "$2" ]; then
        printf "error: Wrong number of arguments!\n"
        return 1
    fi
}


last_field() {
    echo "$(echo "$1" | awk -F '/' '{ print $NF; }')"
}

git_remote_add() {
    check_narg $# 1

    git remote add origin "$1"
}


git_push() {
    check_narg $# 1

    git commit -am "$*"
    git push origin master
}


main() {
    check_narg "$#" "1"
    local passwd="false"
    
    local out="/tmp/git_report.html"
    local config_path=".git/config"
    local tpl="https://bozso:%s@github.com/bozso"
    local nocom="nothing to commit, working tree clean"
    
    
    if [ "all" = "$1" ]; then
        case "$2" in
            "push")
                passwd="true"
                ;;
            "pull")
                passwd="true"
                ;;
            *)
                ;;
        esac
        
        
        if [ "true" = "$passwd" ]; then
            stty -echo
            printf "Password: "
            read pwd
            stty echo
            printf "\n"        
        
        fi
        
        printf "<!DOCTYPE html>\n<html>\n<body>\n" > $out
        printf "<style>\np {white-space: pre-wrap}\n</style>\n" >> $out
        
        for repo in $repos; do
            cd "$repo"
            
            printf "$start_tpl" "$repo"
            
            local address="$(printf "$tpl" "$pwd")"
            
            local url="$(git remote get-url --all origin | \
                         awk -F '/' '{ print $NF; }')"
            
            local url="${address}/${url}"
            
            
            case "$2" in
                "stat")
                    printf "\n<h1> Repository: %s </h1> \n" $repo >> $out
                    local stat="$(git status)"
                    printf "<p>%s</p>\n" "$stat" >> $out
                    printf "$stat"
                    ;;
                "push")
                    local msg="$(git status | awk  'FNR == 2 { print $0 }')"
                    
                    [ "${nocom}" = "${msg}" ] && continue
                    
                    printf "Type in commit message for $(last_field $repo)!\n"
                    git commit -a -F -
                    git push "${url}"
                    ;;
                "pull")
                    git pull "${url}"
                    ;;
                *)
                    printf "Unrecognized option %s!\n" $2 >&2
                    return 1
                    ;;
            esac
            
            printf "$end_tpl" "$repo"
        
        done
        printf "\n</html>\n</body>" >> $out
        
        return 0
    fi
    
    
    case $1 in
        "stat")
            git status
            ;;
        "push")
            shift
            git_push "$@"
            ;;
        "pull")
            git pull origin master
            ;;
        *)
            printf "Unrecognized option %s!\n" $1 >&2
            return 1
            ;;
    esac
}

main "$@"