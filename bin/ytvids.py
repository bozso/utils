#! /usr/bin/env python

from youtube_dl import main
from sys import argv

if __name__ == '__main__':
    url = "https://www.youtube.com/playlist?list=PLdN-rWQpN5Rp5OCjOQsR4RR8Kz7EQAFKy"
    user = "bozsoistvan93@gmail.com"
    
    if argv[1] == "--music":
        cmd = ["--yes-playlist", "-o", "~/Zene/%(title)s.%(ext)s",
               "--username={}".format(user), "-x", url]
    else:
        cmd = ["--yes-playlist", "-o", "~/Videók/%(title)s.%(ext)s",
               "--username={}".format(user), url]
    
    main(cmd)
