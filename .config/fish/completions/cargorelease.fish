function __cargorelease_next_versions
    test -f Cargo.toml; or return
    set -l cargo_version (awk -F'"' '/^version = /{print $2; exit}' Cargo.toml)
    string match -qr '^[0-9]+\.[0-9]+\.[0-9]+$' -- $cargo_version; or return
    set -l parts (string split . -- $cargo_version)
    echo $parts[1].$parts[2].(math $parts[3] + 1)
    echo $parts[1].(math $parts[2] + 1).0
    echo (math $parts[1] + 1).0.0
end

complete -c cargorelease -f
complete -c cargorelease -n '__fish_is_nth_token 1' -a '(__cargorelease_next_versions)' -d 'New version'
