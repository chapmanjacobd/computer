# Defined via `source`
function processes.fzf
    set -f ps_cmd (command -v ps || echo "ps")
    set -f ps_preview_fmt (string join ',' 'pid' 'ppid=PARENT' 'user' '%cpu' 'rss=RSS_IN_KB' 'start=START_TIME' 'command')

    string split --no-empty --field=1 -- " " ($ps_cmd -A -opid,command | \
                _fzf_wrapper --multi \
                            --prompt="Processes> " \
                            --query (commandline --current-token) \
                            --ansi \
                            --header-lines=1 \
                            --preview="$ps_cmd -o '$ps_preview_fmt' -p {1} || echo 'Cannot preview {1} because it exited.'" \
                            --preview-window="bottom:4:wrap" \
                            $fzf_processes_opts
                )

end
