# Defined interactively
function ytdn --wraps='yt'
    cd (d dump/video/)
    yt $argv
end
