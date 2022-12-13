# Defined interactively
function dnfinstall --wraps='dnf install'
    sudo dnf install $argv
    and echo $argv >>~/.github/dnf_installed

    sort --unique --ignore-case ~/.github/dnf_installed | sponge ~/.github/dnf_installed
end
