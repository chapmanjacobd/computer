function log -w journalctl
    journalctl --no-hostname -n5000 -a $argv | grep -v -E 'postfix|Firewall|pam|libva|kioslave|ddcutil|sshd|audit|kwin_core: Applying KScreen config|vsce-sign|ETA: |/dev/tty: No such device or address|making sync progress|dnscrypt-proxy' | less -FSRXc +G
end
