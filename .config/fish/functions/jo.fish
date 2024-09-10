# Defined interactively
function jo
    for f in ~/.local/jobs/*
        systemctl --user status (basename $f)
    end
    for f in ~/.local/jobs/*
        journalctl --user -n5000 --pager-end -u (basename $f)
    end
end
