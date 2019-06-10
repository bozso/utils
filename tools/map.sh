# hash() {
#     echo $((0x$(sha1sum <<<"$1")0))
# }


in_str() {
    local reqsubstr="$1"
    shift
    local string="$@"
    
    if [ -z "${string##*$reqsubstr*}" ]; then
        echo "true"
    else
        echo "false"
    fi
}


key() {
    if [ -n "$1" ]; then
        printf "%s" "$1" | awk -F ':' '{print $1}' 
    else
        printf "%s" | awk -F ':' '{print $1}' 
    fi
}

value() {
    if [ -n "$1" ]; then
        echo "$(printf "%s\n" "$1" | awk -F ':' '{print $NF}'  | tr -d '\n')"
    else
        echo "$(printf "%s\n" | awk -F ':' '{print $NF}' | tr -d '\n')"
    fi
}

mget() {
    local key="$1"
    local table="$2"
    
    for line in $table; do
        if [ "$(in_str "$key" "$line")" = "true" ]; then
            echo "$(value "$line")"
        fi
    done
}
