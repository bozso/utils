from utils.html.tag import *


def main():
    t = \
    div(
        p("a", klass="klass"),
        p("b"),
        div(
            p("c"),
        ),
        controls=True, src="a/b"
    )
    
    print(t.render())

if __name__ == "__main__":
    main()
