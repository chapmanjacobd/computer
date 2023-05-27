function getTabs
    head -10 ~/mc/tabs | xclip -selection c
    sed -i -e 1,10d ~/mc/tabs
end
