function copy-last-command
    history | head -1 | xclip -selection c
end
