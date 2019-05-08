import base64 as b64
import pylatex as pl
import json as js
from os.path import basename

def main():
    paths = ["/home/istvan/Dokumentumok/texfiles/images/SBAS_vs_PSI.jpg",
             "/home/istvan/Dokumentumok/texfiles/images/antropo_colorb.png"]
    
    a = {path: pl.encode_image(path) for path in paths}
    
    with open("test.json", "w") as f:
        js.dump(a, f)
    
    with open("test.json", "r") as f:
        a = js.load(f)
    
    pl.decode_image(a, paths[1])

main()
