# Defined interactively
function nextSongDelete
    if pgrep -f 'lb listen'
        lb next --delete
    else if pgrep -f 'mpv .*/6'
        lb-dev next --delete
    else
        ssh pulse15 lb next --delete
    end
end
