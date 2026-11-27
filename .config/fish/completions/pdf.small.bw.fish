complete -c pdf.small.bw -s r -l resize -x -d 'Resize images to this width (default: 1000)'
complete -c pdf.small.bw -n '__fish_is_nth_token 1' -a '(__fish_complete_directories)' -d 'Directory containing images'
