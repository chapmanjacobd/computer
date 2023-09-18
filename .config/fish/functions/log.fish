function log -w journalctl
    journalctl --no-hostname --reverse -a $argv | grep -v -E 'postfix|Firewall|pam|libva|kioslave|ddcutil' | less -FSRXc
end
