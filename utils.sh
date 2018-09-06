#! /usr/bin/env sh

function update_clean {
    
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    
    sudo apt-get clean
    sudo apt-get autoremove
}

function gstat {
    git status
}
