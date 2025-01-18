# Defined interactively
function dnfremove --wraps='dnf install'
    for arg in $argv
        filterfile ~/.github/dnf_installed $arg
    end
    if command -v rpm-ostree >/dev/null
        sudo rpm-ostree remove $argv
        echo sudo rpm-ostree override remove
    else
        sudo dnf remove $argv
    end
end
