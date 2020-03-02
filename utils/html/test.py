from utils.html import *


def main():
    dd = t.div.With(klass="divine")
    
    d = \
    t.html(
        t.h1("h"),
        dd(
            t.p("a", klass="klass"),
            t.p("b"),
            t.div(
                t.p("c"),
            ),
            
            st.source(src="a.py"),
            t.ul(
                t.li("1"),
                t.li("2"),
            ),
            
            controls=True, src="a/b"
        )
    )
    
    print(d.render())

if __name__ == "__main__":
    main()
