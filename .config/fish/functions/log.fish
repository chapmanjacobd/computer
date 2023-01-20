function log
    journalctl --since "5 minutes ago" $argv | grep -v -E 'postfix|Firewall|pam|syncthing' | less -FSRXc
end
