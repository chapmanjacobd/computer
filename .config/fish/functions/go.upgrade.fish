# Defined interactively
function go.upgrade --argument-names v
    # go.upgrade           # upgrade to the latest stable release
    # go.upgrade 1.27.3    # upgrade to a specific version
    set -l go /usr/local/go/bin/go
    test -x $go; or set go go
    set -l current ($go env GOVERSION 2>/dev/null | string replace -r '^go' '')

    if test -z "$v"; or test "$v" = latest
        set v (curl -fsS 'https://go.dev/VERSION?m=text' | head -n1 | string replace -r '^go' '')
    else
        set v (string replace -r '^go' '' -- $v)
    end

    if test -z "$v"
        echo "go.upgrade: could not determine the latest Go version" >&2
        return 1
    end

    if test "$current" = "$v"
        echo "Go $v is already installed"
        return 0
    end

    set -l arch (uname -m)
    switch $arch
        case x86_64
            set arch amd64
        case aarch64
            set arch arm64
        case armv6l armv7l
            set arch armv6l
    end

    set -l dir (mktemp -d)
    set -l tarball $dir/go$v.linux-$arch.tar.gz

    echo "Upgrading Go $current -> $v"
    if not curl -fsSL --retry 3 -o $tarball https://go.dev/dl/go$v.linux-$arch.tar.gz
        rm -rf $dir
        return 1
    end

    if sudo rm -rf /usr/local/go; and sudo tar -C /usr/local -xzf $tarball
        rm -rf $dir
        $go version
    else
        rm -rf $dir
        return 1
    end
end
