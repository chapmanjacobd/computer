function mpvonce
    mpv "$argv[1]" $argv[2]
    and trash "$argv[1]"
end
