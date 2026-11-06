function _windows.kwin --argument-names operation identifier
    set -l plugin_name (string join '_' fish_windows $fish_pid (random))
    set -l runtime_dir "$XDG_RUNTIME_DIR"
    if test -z "$runtime_dir"
        set runtime_dir /tmp
    end

    set -l js_file (mktemp "$runtime_dir/windows.XXXXXX.js")
    if test $status -ne 0
        printf 'Unable to create a temporary KWin script.\n' >&2
        return 1
    end

    set -l run_id $plugin_name
    switch "$operation"
        case list
            printf '%s\n' \
                "var R=\"$run_id\", US=String.fromCharCode(31);" \
                'function clean(s) { s = "" + s; return s.split(US).join(" ").split("\t").join(" ").split("\n").join(" ").split("\r").join(" "); }' \
                'var wins=workspace.windowList();' \
                'for (var i=0; i<wins.length; i++) {' \
                '    var w=wins[i];' \
                '    if (!w.normalWindow || w.deleted) continue;' \
                '    console.warn(R+US+(""+w.internalId)+US+clean(w.resourceClass)+US+clean(w.resourceName)+US+clean(w.caption));' \
                '}' \
                'console.warn(R+"_END");' >"$js_file"
        case maximize unmaximize
            set -l maximize false
            if test "$operation" = maximize
                set maximize true
            end
            printf '%s\n' \
                'var wins=workspace.windowList();' \
                "for (var i=0; i<wins.length; i++) { var w=wins[i]; if (w.normalWindow && !w.deleted && w.maximizable) w.setMaximize($maximize, $maximize); }" >"$js_file"
        case close
            if test -z "$identifier"
                rm -f -- "$js_file"
                printf 'A KWin window id is required.\n' >&2
                return 1
            end
            if not string match -rq '^[{0-9a-fA-F-]+}$' -- "$identifier"
                rm -f -- "$js_file"
                printf 'Invalid KWin window id: %s\n' "$identifier" >&2
                return 1
            end
            printf '%s\n' \
                "var T=\"$identifier\", wins=workspace.windowList();" \
                'for (var i=0; i<wins.length; i++) { var w=wins[i]; if ((""+w.internalId)===T) { w.closeWindow(); break; } }' >"$js_file"
        case '*'
            rm -f -- "$js_file"
            printf 'Unknown KWin window operation: %s\n' "$operation" >&2
            return 1
    end

    qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "$plugin_name" >/dev/null 2>&1
    set -l script_id (qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$js_file" "$plugin_name" 2>/dev/null)
    if not string match -rq '^[0-9]+$' -- "$script_id"
        rm -f -- "$js_file"
        printf 'Unable to load the KWin window script.\n' >&2
        return 1
    end

    set -l since (date '+%Y-%m-%d %H:%M:%S')
    qdbus org.kde.KWin "/Scripting/Script$script_id" org.kde.kwin.Script.run >/dev/null 2>&1
    if test $status -ne 0
        qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "$plugin_name" >/dev/null 2>&1
        rm -f -- "$js_file"
        printf 'Unable to run the KWin window script.\n' >&2
        return 1
    end

    if test "$operation" = list
        set -l output
        for i in (seq 1 60)
            set output (journalctl --user -o cat -q --since "$since" 2>/dev/null | string match -r -- "$run_id.*")
            if string match -q -- "$run_id"_END $output
                break
            end
            sleep 0.05
        end

        if not string match -q -- "$run_id"_END $output
            qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "$plugin_name" >/dev/null 2>&1
            rm -f -- "$js_file"
            printf 'KWin did not return a window list.\n' >&2
            return 1
        end

        set -l us (printf '\x1f')
        for line in $output
            if string match -q -- "$run_id"_END "$line"
                continue
            end
            set line (string match -r -- "$run_id.*" "$line")
            set -l fields (string split "$us" -- "$line")
            if test (count $fields) -ge 5
                printf '%s\t[%s]\t%s\t%s\n' "$fields[2]" "$fields[3]" "$fields[4]" "$fields[5]"
            end
        end
    end

    qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "$plugin_name" >/dev/null 2>&1
    rm -f -- "$js_file"
end
