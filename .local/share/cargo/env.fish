# rustup shell setup
if not contains "/home/xk/.local/share/cargo/bin" $PATH
    # Prepending path in case a system-installed rustc needs to be overridden
    set -x PATH "/home/xk/.local/share/cargo/bin" $PATH
end
