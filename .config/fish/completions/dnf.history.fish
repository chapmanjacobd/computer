complete -c dnf.history -f
complete -c dnf.history -a '(rpm -qa --qf "%{NAME}\n" 2>/dev/null)' -d 'Installed package'
