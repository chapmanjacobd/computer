# Defined via `source`
function log.each
    for s in (systemctl list-unit-files --type service --state enabled --no-legend --no-pager | cut -f1 -d' ')
        log -u $s
    end

    for s in (systemctl list-unit-files --user --type service --no-legend --no-pager | cut -f1 -d' ')
        log --user -u $s
    end

end
