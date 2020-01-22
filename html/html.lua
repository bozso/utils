--[[ ©2012 Tangent128

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to
do so, subject to the Conditions of the MIT License as specified here:
http://opensource.org/licenses/MIT


Lua 5.2's _ENV functionality naturally expedites some fun syntax tricks;
partly for a side project, and partly for the fun of it, I wrote a
module that creates an _ENV object with a metatable to synthesize
HTML-wrapping functions. Thus,

local _ENV = require"htmlua".new()
return html {
    body {
        div {
            class = "class",
            p "Hello"
        }
    }
}

would yield "<html><body><div
class="class"><p>Hello</p></div></body></html>".


So then, for more fun, I had it generate callable tables instead of raw
functions. As tables, the HTML-wrappers can be further indexed to get
more-specific, class-tagged versions to fit a little more nicely with
today's CSS frameworks:

return html {
    body {
        div.class {
            p "Hello"
        },
        div.two.classes()
    }
}

yields "<html><body><div class=" class"><p>Hello</p></div><div class="
two classes"></div></body></html>"

http://fossil.tangent128.name/LuaForum/artifact/adbc426fafc3cb1f37e0a1a2d7f4f50cc4a498c0

--]]

-- module for easy production of HTML via Lua table constructors
-- nice usage pattern:
--[[
local htmlua = require"path.to.htmlua".new()
local result
-- set userData, htmlData
do _ENV = htmlua
	result = html{
		head {
			title "Page"
		},
		body {
			div.class {
				p {
					"User data: ", userData, " (escaped)"
				},
				p.class {
					"Raw HTML: ", rawHTML(htmlData)
				}
			}
		}
	}
end
-- use tostring(result)

--]]

local concat, tostring, string = table.concat, tostring, string
local setmetatable, getmetatable, pairs, type = setmetatable, getmetatable, pairs, type

local _ENV = {}

local gen_mt, tag_mt, safe_mt, genHTML, safeHTML, escapeHTML, rawHTML

-- create HTML from a table
function genHTML(tag, content)
	
	-- convenience; can call with table or string parameter
	if type(content) == "string" then
		return genHTML(tag, {content})
	end
	
	local name = tag._name
	local tagClass = tag._class
	
	content.class = content.class and ((tagClass or " ") .. content.class) or tagClass or nil
	
	local attTable = {}
	local bodyTable = {}
	for k,v in pairs(content) do
		local t = type(k)
		if t == "string" then
			attTable[#attTable + 1] = ('%s="%s"'):format(k,safeHTML(v))
		elseif t == "number" then
			bodyTable[#bodyTable + 1] = safeHTML(v)
		end
	end
	
	local atts = concat(attTable, " ")
	if #atts > 0 then atts = " " .. atts end
	
	local body = concat(bodyTable)
	
	local html = ("<%s%s>%s</%s>"):format(name, atts, body, name)
	
	return rawHTML(html)
	
end

-- autocreates callable tables that generate HTML for a tag
gen_mt = {
	__index = function(context, name)
		local tag = setmetatable({
			_name = name,
			_class = false
		}, tag_mt)
		context[name] = tag
		return tag
	end
}

-- make callable HTML generating tables, which can be autoindexed
-- for versions which autoadd class attributes
tag_mt = {
	__call = genHTML,
	__index = function(tag, class)
		local oldClass = tag._class or ""
		
		local tagWithClass = setmetatable({
			_name = tag._name,
			_class = oldClass .. " " .. class
		}, tag_mt)
		
		tag[class] = tagWithClass
		return tagWithClass
	end
}

-- make object that wraps a string known to be safe HTML
safe_mt = {
	__tostring = function(self)
		return self.html
	end
}

function rawHTML(html)
	if type(html) == "string" then
		return setmetatable({
			html = html
		}, safe_mt)
	else
		return
	end
end

-- get printable HTML, escaping unless marked to be used raw
function safeHTML(text)
	if getmetatable(text) == safe_mt then
		return text.html
	end
	
	return escapeHTML(text)
end

-- always escape HTML content
function escapeHTML(text)
	-- escape special chars (<, >, ", and &)
	-- double quotes are assumed for attributes
	text = tostring(text):gsub("&", "&amp;")
	text = text:gsub("<", "&lt;")
	text = text:gsub(">", "&gt;")
	text = text:gsub('"', "&quot;")
	
	-- unescape numeric entities and explicit &amp;
	-- disabled due to expected confusion, belongs elsewhere
	--[[   text = text:gsub("&amp;#(x%x+);", "&#%1;")
	text = text:gsub("&amp;#(%d+);", "&#%1;")
	text = text:gsub("&amp;amp;", "&amp;")     ]]
	
	return text
end

-- construct new context
function new()
	return setmetatable({
		rawHTML = rawHTML,
		safeHTML = safeHTML,
		escapeHTML = escapeHTML,
	}, gen_mt)
end

return _ENV
