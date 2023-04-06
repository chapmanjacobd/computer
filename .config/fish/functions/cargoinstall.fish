# Defined interactively
function cargoinstall --wraps='cargo install'
    cargo install $argv
    and echo $argv | string split ' ' >>~/.github/cargo_installed

    sort --unique --ignore-case ~/.github/cargo_installed | sponge ~/.github/cargo_installed
end
