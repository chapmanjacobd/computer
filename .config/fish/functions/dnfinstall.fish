function dnfinstall --wraps='dnf install'
    if command -v rpm-ostree > /dev/null
        sudo rpm-ostree install --apply-live $argv
        and echo $argv | string split ' ' >>~/.github/ostree_installed
        sort --unique --ignore-case ~/.github/ostree_installed | sponge ~/.github/ostree_installed
    else
        sudo dnf install $argv
        and echo $argv | string split ' ' >>~/.github/dnf_installed
        sort --unique --ignore-case ~/.github/dnf_installed | sponge ~/.github/dnf_installed
    end
end
