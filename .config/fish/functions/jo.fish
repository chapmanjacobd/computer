# Defined interactively
function jo
    for f in ~/.local/jobs/*
        # systemctl --user status (basename $f)
        journalctl --user -n5000 --pager-end -u (basename $f)
    end
end
