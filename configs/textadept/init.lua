textadept.editing.auto_indent = true
buffer.tab_width = 4
buffer.use_tabs = false
buffer.edge_column = 79
buffer.edge_mode= buffer.EDGE_LINE
-- textadept.editing.auto_pairs = nil

-- local _L = require('locale')

-- local m_edit = textadept.menu.menubar[_L['_Edit']]
-- local m_sel = m_edit[_L['_Select']]


textadept.file_types.extensions["gpp"] = "ansi_c"
textadept.file_types.extensions["cml"] = "ansi_c"


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
keys["cb"] = textadept.run.compile
keys["cm"] = textadept.editing.block_comment
keys["ck"] = buffer.del_line_left

textadept.run.compile_commands["latex"] = "latexrun %p"
textadept.run.build_commands["latex"] = "latexrun %p"

textadept.run.compile_commands["cpp"] = "ninja"
textadept.run.build_commands["cpp"] = "ninja"
-- textadept.run.compile_commands["cpp"] = "python make.py build_ext --inplace"
-- textadept.run.build_commands["cpp"] = "python make.py build_ext --inplace"
textadept.run.compile_commands["ansi_c"] = "ninja"
textadept.run.compile_commands["fortran"] = "ninja"

local cmd = "sh /home/istvan/progs/utils/menu.sh markdown %p"

textadept.run.run_commands["markdown"] = cmd
textadept.run.run_commands["html"] = cmd
textadept.run.run_commands["cml"] = cmd


--
-- keys.command_mode = {
--    ["h"] = buffer.char_left,
--    ["j"] = buffer.line_down,
--    ["k"] = buffer.line_up,
--    ["l"] = buffer.char_right,
--    ["i"] = enter_edit
--}

-- keys["esc"] = enter_command

-- keys.MODE = "command_mode"

-- textadept.run.build_commands["cpp"] = "ninja"


local property, property_int = buffer.property, buffer.property_int

property['color.white'] = 0xC0C0C0
property['style.default'] = 'fore:$(color.black),back:$(color.white)'
property['style.bracelight'] = 'fore:$(color.white),back:$(color.black)'
property['style.folddisplaytext'] = 'fore:$(color.white),bold'
property['style.linenumber'] = 'fore:$(color.black),back:$(color.white)'

buffer:set_sel_fore(true, property_int['color.white'])
buffer:set_sel_back(true, property_int['color.light_black'])
buffer.caret_fore = property_int['color.grey_black']
buffer.caret_line_back = property_int['color.white']

property['style.class'] = 'fore:$(color.yellow)'
property['style.comment'] = 'fore:$(color.black),bold'
property['style.constant'] = 'fore:$(color.red)'
property['style.embedded'] = '$(style.keyword),back:$(color.black)'
property['style.error'] = 'fore:$(color.red),bold'
property['style.function'] = 'fore:$(color.blue)'
property['style.identifier'] = ''
property['style.keyword'] = 'fore:$(color.white),bold'
property['style.label'] = 'fore:$(color.red),bold'
property['style.number'] = 'fore:$(color.blue)'
property['style.operator'] = 'fore:$(color.yellow)'
property['style.preprocessor'] = 'fore:$(color.magenta)'
property['style.regex'] = 'fore:$(color.green),bold'
property['style.string'] = 'fore:$(color.green)'
property['style.type'] = 'fore:$(color.magenta),bold'
property['style.variable'] = 'fore:$(color.blue),bold'
property['style.whitespace'] = ''
