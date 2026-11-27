complete -c adb.apk.backup -f
complete -c adb.apk.backup -n '__fish_is_nth_token 1' -a user -d 'Back up all user apps'
complete -c adb.apk.backup -n '__fish_is_nth_token 1' -a system -d 'Back up all system apps'
complete -c adb.apk.backup -n '__fish_is_nth_token 1' -a all -d 'Back up all apps'
complete -c adb.apk.backup -n '__fish_is_nth_token 2' -a '(adb devices 2>/dev/null | string match -r "^[^\t ]+\tdevice\$" | string split \t | head -n 1)' -d 'Device serial'
