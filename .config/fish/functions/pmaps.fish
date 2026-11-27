# Defined interactively
function pmaps --wraps='cat'
    begin
        cat /proc/(pgrep -f $argv)/status
        cat /proc/(pgrep -f $argv)/smaps
    end | ov
end
