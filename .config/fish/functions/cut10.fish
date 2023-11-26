function cut10
    head -10 "$argv" | xclip -selection c
    sed -i -e 1,10d "$argv"
end
