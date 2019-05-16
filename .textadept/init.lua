textadept.editing.auto_indent = true
buffer.tab_width = 4
buffer.use_tabs = false
buffer.edge_column = 79
buffer.edge_mode= buffer.EDGE_LINE


-- local _L = require('locale')

-- local m_edit = textadept.menu.menubar[_L['_Edit']]
-- local m_sel = m_edit[_L['_Select']]



function xml()
  local left, right = "<", ">"
  buffer:begin_undo_action()
  for i = 0, buffer.selections - 1 do
    local s, e = buffer.selection_n_start[i], buffer.selection_n_end[i]
    if s == e then
      buffer:set_target_range(buffer:word_start_position(s, true),
                              buffer:word_end_position(e, true))
    else
      buffer:set_target_range(s, e)
    end
    buffer:replace_target(left..buffer.target_text..right..left.."/"..buffer.target_text..right)
    buffer.selection_n_start[i] = buffer.target_end
    buffer.selection_n_end[i] = buffer.target_end
  end
  buffer:end_undo_action()
end


keys["ct"] = xml

keys["ca"] = buffer.home
keys["ce"] = buffer.line_end
keys["am"] = textadept.run.compile
keys["cm"] = textadept.editing.block_comment
keys["ck"] = buffer.del_line_left

textadept.run.compile_commands["latex"] = "latexrun %p"
textadept.run.build_commands["latex"] = "latexrun %p"

textadept.run.compile_commands["cpp"] = "ninja"
textadept.run.compile_commands["ansi_c"] = "ninja"
textadept.run.compile_commands["fortran"] = "ninja"

local cmd = "/home/istvan/progs/utils/dmenu.py markdown --infile=%p"

-- textadept.run.compile_commands["markdown"] = cmd
textadept.run.run_commands["markdown"] = cmd
-- textadept.run.build_commands["cpp"] = "ninja"


buffer:set_theme('light', {font = 'Monospace', fontsize = 14})