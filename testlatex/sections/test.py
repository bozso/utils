from pylatex import *

def main():
    doc = Doc.make_doc(__file__, "test.tex")
    
    if doc is None:
        return 0
    
    doc.usepkg("mhchem", version=4)
    doc.usepkgs("graphics", "amsmath")
    
    doc.title("XI. Geomatika Szeminárium, Sopron 2018", "Lassú felszíni "
    "deformációs folyamatok monitorozása sarokreflektorok és Sentinel-1 "
    "adatok felhasználásával magyarországi teszt területeken")
    doc.author("Bozsó et al.", "Bozsó István, Szűcs Eszter, Bányai László, "
               "Wesztergom Viktor")
    doc.institute("MTA CSFK GGI", "MTA CSFK Geodéziai és Geofizikai Intézet")
    
    doc.start()
    
    doc(vsp(10, unit.pt))
    
    doc(inmath(frac(sym.alpha, sym.gamma)))
    
    with doc.minipage(width=twd(0.5)) as d:
        d.image("test.png", width=twd())
    
    with doc.mode("presentation") as d:
        with d.center() as d:
            with d.frame(title="asd") as d:
                d("\\usetheme{Boadilla}")
                d("\\usecolortheme{default}")
                d(frac(sym.alpha, sym.beta))
    
    with doc.itemize() as d:
        d.item(frac(sym.alpha, sym.gamma), parfrac(sym.beta, sym.alpha))
    
    doc.image("proba.png", width=twd(10))
    
    #doc.compile()
    
    return 0
