local wezterm = require 'wezterm'
local act = wezterm.action
local config = wezterm.config_builder()

-- TODO: https://wezterm.org/multiplexing.html#multiplexing

config.check_for_updates = false

config.max_fps = 48
config.animation_fps = 48

config.audible_bell = 'Disabled'
config.visual_bell = {
    fade_in_function = 'EaseIn',
    fade_in_duration_ms = 200,
    fade_out_function = 'EaseOut',
    fade_out_duration_ms = 150
}
config.colors = {
    visual_bell = '#202020'
}

config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = true
config.switch_to_last_active_tab_when_closing_tab = true
config.hide_tab_bar_if_only_one_tab = true
config.pane_focus_follows_mouse = true
config.enable_scroll_bar = true

config.selection_word_boundary = " \t\n{}[]()\"'`,;:│=&!%"

config.tab_max_width = 60
config.window_decorations = "INTEGRATED_BUTTONS|RESIZE"
config.window_padding = {
    left = 8,
    right = 8,
    top = 12,
    bottom = 8
}

local home = os.getenv("HOME") or os.getenv("USERPROFILE")
local url_regex = [[https?://[^<>"\s{-}\^⟨⟩`│⏎]+]]
local hash_regex = [=[[a-f\d]{4,}|[A-Z_]{4,}]=]
local path_regex = [[~?(?:[-.\w]*/)+[-.\w]*]]

config.quick_select_patterns = {url_regex, path_regex, hash_regex}

local function basename(s)
    return string.gsub(s, "(.*[/\\])(.*)", "%2")
end

local function get_current_working_dir(tab)
    local current_dir = tab.active_pane and tab.active_pane.current_working_dir or {
        file_path = ''
    }
    local HOME_DIR = string.format('file://%s', home)

    return current_dir == HOME_DIR and '.' or basename(current_dir.file_path)
end

wezterm.on('format-window-title', function(tab, pane, tabs, panes, config)
    return get_current_working_dir(tab)
end)

wezterm.on('gui-startup', function(cmd)
    local active_screen = wezterm.gui.screens()["active"]
    local _, _, window = wezterm.mux.spawn_window(cmd or {})

    if active_screen.width <= 724 then
        window:gui_window():maximize()
    else
        local menu_bar_height = 100
        window:gui_window():set_inner_size(active_screen.width / 2, active_screen.height - menu_bar_height)
        window:gui_window():set_position(active_screen.width / 2, 0)
    end
end)

config.front_end = "WebGpu"
config.font = wezterm.font_with_fallback {
    {
      family = 'JetBrains Mono',
    },
    'Consolas',
}
config.harfbuzz_features = {'calt=0', 'clig=0', 'liga=0'} -- no ligatures
config.font_size = 11
config.line_height = 1.05
config.underline_position = -2
config.freetype_load_flags = "NO_HINTING"

config.scrollback_lines = 50000

config.keys = {{
    key = 'PageUp',
    action = act.ScrollByPage(-1)
}, {
    key = 'PageDown',
    action = act.ScrollByPage(1)
}, {
    key = 'RightArrow',
    mods = 'CTRL|SHIFT',
    action = act.ActivateTabRelative(1)
}, {
    key = 'LeftArrow',
    mods = 'CTRL|SHIFT',
    action = act.ActivateTabRelative(-1)
}, {
    key = '`',
    mods = 'ALT',
    action = act.TogglePaneZoomState
}, {
    key = 'Enter',
    mods = 'CTRL|SHIFT',
    action = act.SplitVertical({
        domain = 'CurrentPaneDomain'
    })
}, {
    key = 'w',
    mods = 'CTRL|SHIFT',
    action = act.CloseCurrentPane({
        confirm = true
    })
}, {
    key = "h",
    mods = "CTRL|SHIFT",
    action = act.Search {
        CaseInSensitiveString = ""
    }
}, {
    key = 'a',
    mods = 'CTRL|SHIFT',
    action = wezterm.action_callback(function(win, pane)
        local lines = pane:get_lines_as_text(1000000) -- same as `scrollback_lines`
        win:copy_to_clipboard(lines, 'Clipboard')
    end)
}, {
    key = 'v',
    mods = 'CTRL',
    action = act.PasteFrom 'Clipboard'
}, {
    key = "LeftArrow",
    mods = "CTRL|ALT",
    action = act.MoveTabRelative(-1)
}, {
    key = "RightArrow",
    mods = "CTRL|ALT",
    action = act.MoveTabRelative(1)
}, {
    key = "RightArrow",
    mods = "CTRL|SHIFT|ALT",
    action = wezterm.action_callback(function(win, pane)
        local tab, window = pane:move_to_new_tab()
    end)
}, { key = 'c',
    mods = 'CTRL',
    action = wezterm.action_callback(function(window, pane)
			local has_selection = window:get_selection_text_for_pane(pane) ~= ""
			if has_selection then
				window:perform_action(act.CopyTo("Clipboard"), pane)
				window:perform_action(act.ClearSelection, pane)
			else
				window:perform_action(act.SendKey { key = 'c', mods = 'CTRL' }, pane)
			end
		end)
}
}

config.mouse_bindings = {{
    event = {
        Up = {
            streak = 1,
            button = 'Left'
        }
    },
    mods = 'NONE',
    action = act.CompleteSelection('Clipboard')
}, {
    event = {
        Up = {
            streak = 1,
            button = 'Left'
        }
    },
    mods = 'CTRL',
    action = act.OpenLinkAtMouseCursor
}, {
    event = {
        Down = {
            streak = 1,
            button = "Right"
        }
    },
    mods = "NONE",
    action = act({
        PasteFrom = "Clipboard"
    })
}}

config.inactive_pane_hsb = {
    saturation = 0.3,
    brightness = 0.6
}

local medium_contrast = wezterm.color.get_builtin_schemes()['Google Light (Gogh)']
medium_contrast.background = '#cebdab'
medium_contrast.foreground = '#000000'
medium_contrast.selection_fg = '#cebdab'
medium_contrast.selection_bg = 'rgba(15%, 15%, 15%, 60%)'
medium_contrast.cursor_fg = "#73635a"
medium_contrast.ansi = {"#000000", -- black
"#8c0000", -- red
"#007d00", -- green
"#8c7000", -- yellow
"#003cb4", -- blue
"#820082", -- magenta
"#008b8b", -- cyan
"#888888" -- white
}
medium_contrast.brights = {"#545454", -- bright black
"#ff0000", -- bright red
"#00c300", -- bright green
"#ffff00", -- bright yellow
"#0000ff", -- bright blue
"#ff00ff", -- bright magenta
"#00cdcd", -- bright cyan
"#ffffff" -- bright white
}
medium_contrast.compose_cursor = 'orange'

config.color_schemes = {
    ['Medium Contrast'] = medium_contrast
}
config.color_scheme = 'Medium Contrast'

return config
