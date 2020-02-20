from utils.html.tag import *


def main():
    t = div(p("a"), p("b"), controls=True, src="a/b")
    
    print(t.render())

if __name__ == "__main__":
    main()
