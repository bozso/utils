from pylatex.base import Doc

def main():
    doc = Doc(__file__, "test.tex")
    
    if doc is None:
        return 0
    
    doc.usepkg("mhchem", version=4)
    
    with doc.mode("presentation") as d:
        with d.begin("center") as d:
            with d.frame(title="asd") as d:
                d("\\usetheme{Boadilla}")
                d("\\usecolortheme{default}")
    
    return 0

if __name__ == "__main__":
    main()
