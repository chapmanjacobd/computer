# Defined interactively
function nextSongDelete
    if pgrep -f 'lb listen'
        lb next --delete-file
    else if pgrep -f 'mpv .*/6'
        lb-dev next --delete-files
    else
        ssh pulse15 lb next --delete-file
    end
end
