local lexer = require('lexer')
local token, word_match = lexer.token, lexer.word_match
local P, R, S = lpeg.P, lpeg.R, lpeg.S

local lex = lexer.new('haxe')

-- Whitespace.
lex:add_rule('whitespace', token(lexer.WHITESPACE, lexer.space^1))

-- Keywords.
lex:add_rule('keyword', token(lexer.KEYWORD, word_match[[
  abstract break case cast catch class continue default do dynamic else enum
  extends extern false final for function if implements import in inline
  interface macro new null operator overload override package private public
  return static switch this throw true try typedef untyped using var while
]]))

-- Types.
lex:add_rule('type', token(lexer.TYPE, word_match[[
  Bool Float Int Void Null String
]]))


-- Strings.
local sq_str = P('L')^-1 * lexer.delimited_range("'", true)
local dq_str = P('L')^-1 * lexer.delimited_range('"', true)
lex:add_rule('string', token(lexer.STRING, sq_str + dq_str))

-- Identifiers.
lex:add_rule('identifier', token(lexer.IDENTIFIER, lexer.word))

-- Comments.
local line_comment = '//' * lexer.nonnewline_esc^0
local block_comment = '/*' * (lexer.any - '*/')^0 * P('*/')^-1
lex:add_rule('comment', token(lexer.COMMENT, line_comment + block_comment))

-- Numbers.
local dec = lexer.digit^1 * ("'" * lexer.digit^1)^0
local hex = '0' * S('xX') * lexer.xdigit^1 * ("'" * lexer.xdigit^1)^0
local bin = '0' * S('bB') * S('01')^1 * ("'" * S('01')^1)^0
local integer = S('+-')^-1 * (hex + bin + dec)
lex:add_rule('number', token(lexer.NUMBER, lexer.float + integer))

-- Preprocessor.
local preproc_word = word_match[[
  define elif else endif error if ifdef ifndef import line pragma undef using
  warning
]]

lex:add_rule('preprocessor',
             #lexer.starts_line('#') *
             (token(lexer.PREPROCESSOR, '#' * S('\t ')^0 * preproc_word) +
              token(lexer.PREPROCESSOR, '#' * S('\t ')^0 * 'include') *
              (token(lexer.WHITESPACE, S('\t ')^1) *
               token(lexer.STRING,
                     lexer.delimited_range('<>', true, true)))^-1))

-- Decorators.
lex:add_rule('decorator', token('decorator', '@:' * lexer.nonnewline^0))
lex:add_style('decorator', lexer.STYLE_PREPROCESSOR)

-- Operators.
lex:add_rule('operator', token(lexer.OPERATOR, S('+-/*%<>!=^&|?~:;,.()[]{}')))

-- Fold points.
lex:add_fold_point(lexer.PREPROCESSOR, 'if', 'endif')
lex:add_fold_point(lexer.PREPROCESSOR, 'ifdef', 'endif')
lex:add_fold_point(lexer.PREPROCESSOR, 'ifndef', 'endif')
lex:add_fold_point(lexer.OPERATOR, '{', '}')
lex:add_fold_point(lexer.COMMENT, '/*', '*/')
lex:add_fold_point(lexer.COMMENT, '//', lexer.fold_line_comments('//'))

return lex
