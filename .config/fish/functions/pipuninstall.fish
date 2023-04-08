# Defined interactively
function pipuninstall --wraps='pip uninstall'
    for arg in $argv
        filterfile ~/.github/pip_installed $arg
    end
    pip uninstall -y $argv
end
