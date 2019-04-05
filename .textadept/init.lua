textadept.editing.auto_indent = true
buffer.tab_width = 4
buffer.use_tabs = false

keys["cb"] = textadept.run.compile
keys["cm"] = textadept.editing.block_comment
keys["ck"] = buffer.del_line_left
textadept.run.compile_commands["latex"] = "latexrun %p"
textadept.run.build_commands["latex"] = "latexrun %p"

buffer:set_theme('light', {font = 'Monospace', fontsize = 14})