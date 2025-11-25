# Defined interactively
function dnfremove --wraps='dnf install'
    for arg in $argv
        file.lines.filter ~/.github/dnf_installed $arg
    end
    if command -v rpm-ostree >/dev/null
        sudo rpm-ostree remove $argv
        echo sudo rpm-ostree override remove
    else
        sudo dnf remove $argv
    end
end
