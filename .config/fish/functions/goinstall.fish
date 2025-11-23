# Defined interactively
function goinstall --wraps='go install'
    go install $argv
    and echo $argv | string split ' ' >>~/.github/go_installed

    sort --unique --ignore-case ~/.github/go_installed | sponge ~/.github/go_installed
end
