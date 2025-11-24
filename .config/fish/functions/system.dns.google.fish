function system.dns.google
    set conName (coalesce "$argv" (nmcli -t -f NAME,TIMESTAMP con show | sort -t: -nk2 | tail -n1 | cut -d: -f1 | sed -e 's/[[:space:]]*$//'))
    nmcli con mod "$conName" ipv4.dns "1.1.1.1 8.8.8.8"
    nmcli con mod "$conName" ipv4.ignore-auto-dns yes
    nmcli con down "$conName"
    nmcli con up "$conName"
end
