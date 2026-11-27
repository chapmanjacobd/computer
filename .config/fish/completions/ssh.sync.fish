complete -c ssh.sync -f
complete -c ssh.sync -n '__fish_is_nth_token 1' -d 'Tmux session name'
complete -c ssh.sync -n 'not __fish_is_nth_token 1' -a '(__fish_complete_command)' -d 'Command'
