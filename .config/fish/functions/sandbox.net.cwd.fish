function sandbox.net.cwd --description 'Run a command with network, writable CWD, and a temporary home'
    command bwrap \
        --unshare-all --share-net --new-session --die-with-parent \
        --cap-drop ALL --clearenv \
        --ro-bind /usr /usr \
        --ro-bind /bin /bin \
        --ro-bind /lib /lib \
        --ro-bind-try /lib64 /lib64 \
        --ro-bind-try /etc/ld.so.cache /etc/ld.so.cache \
        --ro-bind /etc/resolv.conf /etc/resolv.conf \
        --ro-bind /etc/hosts /etc/hosts \
        --ro-bind /etc/nsswitch.conf /etc/nsswitch.conf \
        --ro-bind /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt \
        --setenv SSL_CERT_FILE /etc/ssl/certs/ca-certificates.crt \
        --setenv CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt \
        --proc /proc --dev /dev --tmpfs /tmp \
        --dir /home/sandbox \
        --setenv HOME /home/sandbox \
        --setenv PATH /usr/bin:/bin \
        --bind "$PWD" /work \
        --chdir /work \
        -- $argv
end
