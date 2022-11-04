complete -c reddit-add -f -k -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -c reddit-add -k -a "(cat ~/mc/*reddit.txt)"
complete -c reddit-links-update -f
complete -c reddit-links-update -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -c reddit-get-sounds -f
complete -c reddit-get-sounds -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -c reddit-get-videos -f
complete -c reddit-get-videos -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -c reddit-get-photos -f
complete -c reddit-get-photos -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
