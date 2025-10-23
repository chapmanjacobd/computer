function dnfinstall --wraps='dnf install'
    if type -q rpm-ostree
        sudo rpm-ostree install $argv
        and echo $argv | string split ' ' >>~/.github/ostree_installed
        sort --unique --ignore-case ~/.github/ostree_installed | sponge ~/.github/ostree_installed
    else if type -q apt
        sudo apt install $argv
        and echo $argv | strings split ' ' >>~/.github/apt_installed
        sort --unique --ignore-case ~/.github/apt_installed | sponge ~/.github/apt_installed
    else
        sudo dnf install $argv
        and echo $argv | string split ' ' >>~/.github/dnf_installed
        sort --unique --ignore-case ~/.github/dnf_installed | sponge ~/.github/dnf_installed
    end
end
