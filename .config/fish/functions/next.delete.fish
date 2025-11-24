# Defined interactively
function next.delete
    if pgrep -f 'lb listen'; or pgrep -f 'lb lt'
        lb next --delete-file
    else if pgrep -f 'mpv .*mpv_socket'
        lb next --delete-files
    else
        ssh len lb next --delete-file
    end
end
