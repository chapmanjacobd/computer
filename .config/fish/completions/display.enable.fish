complete -c display.enable -f
complete -c display.enable -n '__fish_is_nth_token 1' -a '(kscreenctl list-outputs --names 2>/dev/null)' -d 'Output name'
