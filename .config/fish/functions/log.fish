function log -w journalctl
    journalctl --no-hostname --reverse -a $argv | grep -v -E 'postfix|Firewall|pam|libva|kioslave|ddcutil|sshd|audit|kwin_core: Applying KScreen config' | less -FSRXc
end
