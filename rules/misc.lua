--[[
Copyright (c) 2011-2015, Vsevolod Stakhov <vsevolod@highsecure.ru>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
]]--

-- This is main lua config file for rspamd

local util = require "rspamd_util"

local reconf = config['regexp']


-- Uncategorized rules

-- Local rules
local r_bgcolor = '/BGCOLOR=/iP'
local r_font_color = '/font color=[\\"\']?\\#FFFFFF[\\"\']?/iP'
reconf['R_WHITE_ON_WHITE'] = string.format('(!(%s) & (%s))', r_bgcolor, r_font_color)
reconf['R_FLASH_REDIR_IMGSHACK'] = '/^(?:http:\\/\\/)?img\\d{1,5}\\.imageshack\\.us\\/\\S+\\.swf/U'

-- Different text parts
rspamd_config.R_PARTS_DIFFER = function(task)
  local distance = task:get_mempool():get_variable('parts_distance', 'int')

  if distance then
    local nd = tonumber(distance)

    if nd < 50 then
      local score = 1 - util.tanh(nd / 100.0)

      task:insert_result('R_PARTS_DIFFER', score, tostring(nd) .. '%')
    end
  end

  return false
end

-- Date issues
rspamd_config.MISSING_DATE = function(task)
	if rspamd_config:get_api_version() >= 5 then
		if not task:get_header_raw('Date') then
			return true
		end
	end

	return false
end
rspamd_config.DATE_IN_FUTURE = function(task)
	if rspamd_config:get_api_version() >= 5 then
		local dm = task:get_date{format = 'message'}
		local dt = task:get_date{format = 'connect'}
		-- An 2 hour
		if dm > 0 and dm - dt > 7200 then
			return true
		end
	end

	return false
end
rspamd_config.DATE_IN_PAST = function(task)
	if rspamd_config:get_api_version() >= 5 then
    local dm = task:get_date{format = 'message', gmt = true}
    local dt = task:get_date{format = 'connect', gmt = true}
		-- A day
		if dm > 0 and dt - dm > 86400 then
			return true
		end
	end

	return false
end
