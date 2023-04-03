local utils = require 'mp.utils'

function display_error()
  mp.msg.warn("Subtitle download failed: ")
  mp.osd_message("Subtitle download failed")
end

function load_sub_fn(langs)
  return function()
    path = mp.get_property("path")
    print(path)
    path = path:gsub("[%-_ ]*%[[%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_][%w%-_]%](%.%w%w%w%w?)$", '%1')
    print(path)

    -- Subtitles
    t = { args = { "subliminal", "--opensubtitles", "xk3", "idiZQc2kVyvsQk8!", "download", "-s", "-f" } }
    for i = 1, #langs do
      table.insert(t.args, "-l")
      table.insert(t.args, langs[i])
    end
    table.insert(t.args, path)

    mp.osd_message("Searching subtitles")
    res = utils.subprocess(t)
    if res.error == nil then
      for i = 1, #langs do
        srt_path = string.gsub(path, "%.%w+$", "." .. langs[i] .. ".srt")
        if mp.commandv("sub_add", srt_path) then
          mp.msg.warn("Subtitle download succeeded")
          mp.osd_message("Subtitle '" .. srt_path .. "' download succeeded")
        else
          display_error()
        end
      end
    else
      display_error()
    end
  end
end

mp.add_key_binding("ctrl+j", "auto_load_subs_en", load_sub_fn({"en"}))
mp.add_key_binding("ctrl+alt+j", "auto_load_subs_zh", load_sub_fn({"zt", "ze", "zh"}))
