# Defined interactively
function ps.fzf.pause
    ps.pause (ps --no-headers -weo pid,stat,command ww | awk '$2 !~ /^T/ && $3 !~ /^([[])/ { $2=""; print $0 }' | grep -i "$argv" | fzf.choose | cut -d' ' -f1)
end
