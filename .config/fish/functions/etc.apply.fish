function etc.apply --description 'Copy ~/.github/etc to /etc, showing a diff before overwriting anything'
    argparse -n etc.apply 'n/dry-run' 'r/reload' 'v/verbose' 'h/help' -- $argv
    or return 2

    if set -q _flag_help
        printf '%s\n' \
            'usage: etc.apply [--dry-run] [--reload] [--verbose]' \
            '' \
            'Copy ~/.github/etc to /etc, printing a diff of every file before' \
            'overwriting it. --reload also runs the safe reload commands for' \
            'changed systemd, sysctl, journald, and sshd config.'
        return 0
    end

    set -l src_root ~/.github/etc
    if not test -d $src_root
        echo "etc.apply: $src_root does not exist" >&2
        return 1
    end

    set -l changed
    set -l unchanged 0

    for src in (find $src_root -type f | sort)
        set -l rel (string replace -- "$src_root/" '' $src)
        set -l dest /etc/$rel

        if test -e $dest; and cmp -s -- $src $dest
            set unchanged (math $unchanged + 1)
            if set -q _flag_verbose
                printf '= %s\n' $dest
            end
            continue
        end

        set -a changed $rel
    end

    if not set -q changed[1]
        printf 'All %d files already match.\n' $unchanged
        return 0
    end

    # Show the old /etc file first so the terminal log records anything that is
    # about to be clobbered.
    for rel in $changed
        set -l src $src_root/$rel
        set -l dest /etc/$rel

        if test -e $dest
            printf '\n~ %s\n' $dest
            diff --unified --color=auto --label $dest --label $src -- $dest $src
        else
            printf '\n+ %s\n' $dest
            diff --unified --color=auto --label /dev/null --label $src -- /dev/null $src
        end
    end

    if set -q _flag_dry_run
        printf '\n%d file(s) would change; nothing written (--dry-run).\n' (count $changed)
        return 0
    end

    for rel in $changed
        set -l src $src_root/$rel
        set -l dest /etc/$rel
        set -l mode (stat -c %a -- $src)

        sudo install -D -m $mode -o root -g root -- $src $dest
        or return 1

        if command -q restorecon
            sudo restorecon -- $dest
        end
    end

    printf '\nApplied %d file(s).\n' (count $changed)

    set -l reloads
    if string match -q 'systemd/*' $changed
        set -a reloads 'sudo systemctl daemon-reload'
    end
    if string match -q 'sysctl.d/*' $changed
        set -a reloads 'sudo sysctl --system'
    end
    if string match -q 'systemd/journald.conf.d/*' $changed
        set -a reloads 'sudo systemctl restart systemd-journald'
    end
    if string match -q 'ssh/sshd_config.d/*' $changed
        set -a reloads 'sudo sshd -t && sudo systemctl reload sshd'
    end

    if set -q reloads[1]
        if set -q _flag_reload
            for cmd in $reloads
                echo "> $cmd"
                eval $cmd
            end
        else
            printf '\nReload to apply (or rerun with --reload):\n'
            for cmd in $reloads
                printf '  %s\n' $cmd
            end
        end
    end

    if string match -q 'systemd/zram-generator.conf.d/*' $changed
        printf '\nzram: size and compression only change when the device is recreated (reboot).\n'
    end
end
