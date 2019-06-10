#! /usr/bin/env sh

check_narg() {
    if [ "$1" -lt "$2" ]; then
        perr "error: Wrong number of arguments!"
        return 1
    fi
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
    
    case $1 in
        "stat")
            git status
            ;;
        "push")
            shift
            echo "$@"
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