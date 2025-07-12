function log -w journalctl
    journalctl --no-hostname -n5000 -a $argv | grep -v -E 'postfix|Firewall|pam|libva|kioslave|ddcutil|sshd|audit|kwin_core: Applying KScreen config|vsce-sign|ETA: |/dev/tty: No such device or address|making sync progress|dnscrypt-proxy|]: Start|tailscale|was already loaded or has a fragment file|directory has been deleted on a remote device but contains ignored|memory peak|running basic garbage collection|systemd-hostnamed.service: Deactivated successfully|: Failed to sync' | less -FSRXc +G
end
