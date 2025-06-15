# Defined interactively
function jo
    set -x SYSTEMD_COLORS 1

    for f in ~/.local/jobs/*
        systemctl --user --lines=0 status --no-pager (basename $f)
    end | ov
    for f in ~/.local/jobs/*
        journalctl --user -n5000 --pager-end -u (basename $f)
    end
end
