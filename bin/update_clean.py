#! /usr/bin/env python
from utils import cmd

def main():
    cmd("sudo apt-get update")
    cmd("sudo apt-get upgrade")
    cmd("sudo apt-get dist-upgrade")
    
    cmd("sudo apt-get clean")
    cmd("sudo apt-get autoremove")

if __name__ == "__main__":
    main()
