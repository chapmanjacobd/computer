# Defined interactively
function sudocp --argument-names from --argument-names to
    sudo rsync --chown=(stat -c '%U:%G' "$to") "$from" "$to"
end
