# Defined interactively
function catt.default --wraps='git'
    git config --file=/home/xk/.config/catt/catt.cfg options.device "$argv"
end
