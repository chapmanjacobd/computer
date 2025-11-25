function files.modified.last

    find /etc -type f -printf '%TY-%Tm-%Td %TT %p\n' | sort
end
