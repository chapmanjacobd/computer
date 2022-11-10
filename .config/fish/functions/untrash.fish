function untrash
    #mv -iv ~/.local/share/Trash/files/$argv[1] ./

    mv -iv ~/.local/share/Trash/files/(ls -snew -G  /home/xk/.local/share/Trash/files/  | tail -1) "./$argv"
end
