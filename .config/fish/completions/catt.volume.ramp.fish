complete -c catt.volume.ramp -f
complete -c catt.volume.ramp -n '__fish_is_nth_token 1' -a '(seq 1 100)' -d 'Target volume (1-100)'
