# Defined interactively
function cargouninstall --wraps='cargo uninstall'
    for arg in $argv
        file.lines.filter ~/.github/cargo_installed $arg
    end
    cargo uninstall $argv
end
