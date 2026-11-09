function sandbox --description 'Run a command offline with read-only CWD and a temporary home'
    command bwrap \
        --unshare-all --new-session --die-with-parent \
        --cap-drop ALL --clearenv \
        --ro-bind /usr /usr \
        --ro-bind /bin /bin \
        --ro-bind /lib /lib \
        --ro-bind-try /lib64 /lib64 \
        --ro-bind-try /etc/ld.so.cache /etc/ld.so.cache \
        --proc /proc --dev /dev --tmpfs /tmp \
        --dir /home/sandbox \
        --setenv HOME /home/sandbox \
        --setenv PATH /usr/bin:/bin \
        --ro-bind "$PWD" /work \
        --chdir /work \
        -- $argv
end
