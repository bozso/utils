local h = require "html".new()

a = h.html {
        h.body {
            h.div {
                class = "class",
                h.p "Hello",
                h.p "Hello",
                h.p[[
                    Hello
                    aaaa
                    bbb
                ]]
            },
            
            h.header{
                h.meta{charset="utf-8"},
                h.meta{name="viewport", content="width=device-width, initial-scale=1"},
                h.link{rel="stylesheet", href="/home/istvan/Dokumentumok/texfiles/shower/themes/material/styles/styles.css"},
                h.link{rel="stylesheet", href="/home/istvan/Dokumentumok/texfiles/css/notes.css"}
            }
        }
}

print(a)
