# Defined interactively
function dnfremove --wraps='dnf install'
    for arg in $argv
        filterfile ~/.github/dnf_installed $arg
    end
    sudo dnf remove $argv
end
