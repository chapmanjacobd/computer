# Defined via `source`
function file.desktop.create
    set command_name (string replace -r ' ' '_' "$argv")
    set launcher_path $HOME/.local/share/applications/$command_name.desktop

    echo "[Desktop Entry]" >$launcher_path
    echo "Version=1.0" >>$launcher_path
    echo "Type=Application" >>$launcher_path
    echo "Name=$command_name" >>$launcher_path
    echo "Exec=setsid -f fish -c '$argv'" >>$launcher_path
    echo "Terminal=false" >>$launcher_path
    echo "Categories=Utility;" >>$launcher_path

    echo Launcher created:
    echo "$launcher_path"
end
