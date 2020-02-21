from utils.html.tag import *


def main():
    d = \
    t.div(
        t.p("a", klass="klass"),
        t.p("b"),
        t.div(
            t.p("c"),
        ),
        
        
        t.ul(
            t.li("1"),
            t.li("2"),
        ),
        
        controls=True, src="a/b"
    )
    
    print(d.render())

if __name__ == "__main__":
    main()
