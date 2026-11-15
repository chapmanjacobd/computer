function brightness.lg.set
    set -l values (string join ' ' (string escape -- $argv))
    _brightness.lg_lock "_brightness.lg_write $values"
end
