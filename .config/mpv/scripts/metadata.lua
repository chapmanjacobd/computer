local mp = require 'mp'
local utils = require 'mp.utils'

local o = {
    key_toggle = "p",
    key_scroll_up = "UP",
    key_scroll_down = "DOWN",
    font_size = 9,
    border_size = 0.8,
    font = "",
    font_color = "FFFFFF",
    border_color = "000000",
    scroll_lines = 3,
    max_line_width = 100,  -- Maximum characters per line before wrapping
}

require 'mp.options'.read_options(o, "metadata")

-- State
local display_active = false
local scroll_offset = 0
local content_lines = {}
local scroll_bound = false

-- Styling
local function text_style()
    local style = string.format("{\\r\\an7\\fs%d\\bord%.2f", o.font_size, o.border_size)

    if o.font ~= "" then
        style = style .. "\\fn" .. o.font
    end

    if o.font_color ~= "" then
        style = style .. "\\1c&H" .. o.font_color .. "&"
    end

    if o.border_color ~= "" then
        style = style .. "\\3c&H" .. o.border_color .. "&"
    end

    return style .. "}"
end


-- Format timestamp
local function format_timestamp(unix_time)
    if not unix_time or unix_time <= 0 then return "N/A" end
    return os.date("%Y-%m-%d %H:%M", unix_time)
end

-- Escape ASS special characters
local function ass_escape(str)
    if not str then return "" end
    return mp.command_native({"escape-ass", tostring(str)})
end

-- Word wrap text to max_width characters, returns array of lines
local function wrap_text(text, max_width)
    if not text or text == "" then return {""} end

    local lines = {}
    local current_line = ""

    -- Split by existing newlines first
    for paragraph in text:gmatch("[^\r\n]+") do
        -- Split paragraph into words
        for word in paragraph:gmatch("%S+") do
            local test_line = current_line == "" and word or (current_line .. " " .. word)

            if #test_line > max_width then
                if current_line ~= "" then
                    table.insert(lines, current_line)
                    current_line = word
                else
                    -- Single word longer than max_width, just add it
                    table.insert(lines, word)
                    current_line = ""
                end
            else
                current_line = test_line
            end
        end

        if current_line ~= "" then
            table.insert(lines, current_line)
            current_line = ""
        end
    end

    return lines
end

-- Add a line with optional wrapping
local function add_line(lines_table, text, prefix, max_width)
    prefix = prefix or ""
    max_width = max_width or o.max_line_width

    -- Strip ASS codes from prefix to get visual length
    local plain_prefix = prefix:gsub("{\\.-}", "")

    if text and text ~= "" then
        local wrapped = wrap_text(text, max_width - #plain_prefix)
        for i, line in ipairs(wrapped) do
            if i == 1 then
                table.insert(lines_table, prefix .. line)
            else
                -- Indent continuation lines to align with first line content
                table.insert(lines_table, string.rep(" ", #plain_prefix) .. line)
            end
        end
    else
        table.insert(lines_table, prefix)
    end
end

local function get_file_mtime(path)
    local file_date = mp.get_property_number("file-date")
    if file_date then
        return file_date
    end

    if not path or not path:match("^/") then
        -- only do stat for local paths
        return nil
    end

    local res = mp.command_native({
        name = "subprocess",
        args = {"stat", "-c", "%Y", path},
        capture_stdout = true,
        capture_stderr = false
    })

    if res and res.status == 0 and res.stdout then
        local ts = tonumber(res.stdout)
        if ts then
            return ts
        end
    end

    return nil
end

local function normalize_text(s)
    return (s or "")
        :gsub("%s+",  "")       -- collapse all whitespace
        :lower()                -- case-insensitive
end

-- Build metadata content
local function build_metadata()
    content_lines = {}
    local b1 = "{\\b1}"
    local b0 = "{\\b0}"

    local path = mp.get_property("path", "N/A")
    add_line(content_lines, ass_escape(path), b1 .. "Path:" .. b0 .. " ")

    local duration = mp.get_property_number("duration")
    if duration then
        table.insert(content_lines, b1 .. "Duration:" .. b0 .. " " .. mp.format_time(duration))
    end

    local mtime = get_file_mtime(path)
    if mtime then
        table.insert(content_lines, b1 .. "Modified:" .. b0 .. " " .. format_timestamp(mtime))
    end

    local metadata = mp.get_property_native("metadata")
    if metadata and type(metadata) == "table" then
        local hidden_keys = {
            ["compatible_brands"] = true,
            ["major_brand"] = true,
            ["minor_version"] = true,
            ["encoder"] = true,
            ["synopsis"] = true,
            ["purl"] = true,
        }
        local keys = {}
        for k, v in pairs(metadata) do
            if not hidden_keys[k:lower()] and v and v ~= "" then
                table.insert(keys, k)
            end
        end

        -- Sort by value length
        table.sort(keys, function(a, b)
            return #tostring(metadata[a] or "") < #tostring(metadata[b] or "")
        end)

        for _, key in ipairs(keys) do
            local value = metadata[key]
            if value and value ~= "" then
                -- Format key nicely (capitalize first letter, replace _ with space)
                local display_key = key:gsub("^%l", string.upper):gsub("_", " ")
                local prefix = b1 .. ass_escape(display_key) .. ":" .. b0 .. " "
                add_line(content_lines, ass_escape(tostring(value)), prefix)
            end
        end
    else
        table.insert(content_lines, "(No metadata available)")
    end

    -- Track information
    table.insert(content_lines, "")
    table.insert(content_lines, b1 .. "TRACKS" .. b0)
    table.insert(content_lines, "")

    local tracks = mp.get_property_native("track-list")
    if tracks then
        for _, track in ipairs(tracks) do
            local track_type = track.type:sub(1,1):upper() .. track.type:sub(2)
            local track_info = string.format("%s #%d", track_type, track.id)

            if track.title then
                track_info = track_info .. ": " .. ass_escape(track.title)
            end

            if track.lang then
                track_info = track_info .. " [" .. track.lang .. "]"
            end

            if track.codec then
                track_info = track_info .. " (" .. track.codec .. ")"
            end

            local prefix = track.selected and "→ " or "  "
            add_line(content_lines, track_info, prefix)
        end
    end
end

local function show_metadata()
    local max_lines = 20  -- Approximate lines that fit on screen
    local total = #content_lines

    if total == 0 then
        scroll_offset = 0
        mp.set_osd_ass(0, 0, "")
        mp.msg.info("No metadata lines to display (total = 0). Cleared OSD.")
        return
    end

    local max_offset = math.max(0, total - max_lines)
    if scroll_offset > max_offset then
        -- mp.msg.info(string.format("scroll_offset (%d) > max_offset (%d), snapping to end", scroll_offset, max_offset))
        scroll_offset = max_offset
    end

    -- Build visible content
    local visible = {}
    local start_line = scroll_offset + 1
    local end_line = math.min(total, start_line + max_lines - 1)

    for i = start_line, end_line do
        table.insert(visible, content_lines[i])
    end

    local output = text_style() .. table.concat(visible, "\\N")
    mp.set_osd_ass(0, 0, output)

    -- mp.msg.info(string.format("Displaying lines %d-%d of %d (offset: %d, max_offset: %d)", start_line, end_line, total, scroll_offset, max_offset))
end

local function clear_display()
    mp.set_osd_ass(0, 0, "")
end

local function scroll_up()
    if not display_active then return end
    scroll_offset = math.max(0, scroll_offset - o.scroll_lines)
    -- mp.msg.info("Scrolling up to offset: " .. scroll_offset)
    show_metadata()
end

local function scroll_down()
    if not display_active then return end
    -- Don't clamp here; let show_metadata() decide if we need to snap to the end.
    scroll_offset = scroll_offset + o.scroll_lines
    -- mp.msg.info("Scrolling down to offset: " .. scroll_offset)
    show_metadata()
end

local function bind_scroll_keys()
    if not scroll_bound then
        mp.add_forced_key_binding(o.key_scroll_up, "__metadata_scroll_up", scroll_up, {repeatable=true})
        mp.add_forced_key_binding(o.key_scroll_down, "__metadata_scroll_down", scroll_down, {repeatable=true})
        scroll_bound = true
    end
end

local function unbind_scroll_keys()
    if scroll_bound then
        mp.remove_key_binding("__metadata_scroll_up")
        mp.remove_key_binding("__metadata_scroll_down")
        scroll_bound = false
    end
end

local function toggle_display()
    display_active = not display_active

    if display_active then
        scroll_offset = 0
        build_metadata()
        bind_scroll_keys()
        show_metadata()
    else
        unbind_scroll_keys()
        clear_display()
    end
end

mp.add_key_binding(o.key_toggle, "metadata-toggle", toggle_display)

-- Reset on file change
mp.observe_property("path", "string", function()
    if display_active then
        display_active = false
        unbind_scroll_keys()
        clear_display()
    end
    scroll_offset = 0
end)

-- Clean up on shutdown
mp.register_event("shutdown", function()
    unbind_scroll_keys()
    clear_display()
end)
