function etc.apply --description 'Copy ~/.github/etc to /etc, reviewing each diff before overwriting'
    argparse -n etc.apply 'n/dry-run' 'y/yes' 'r/reload' 'v/verbose' 'h/help' -- $argv
    or return 2

    if set -q _flag_help
        printf '%s\n' \
            'usage: etc.apply [--dry-run] [--yes] [--reload] [--verbose]' \
            '' \
            'Show a unified diff for every file that differs from /etc, then' \
            'copy ~/.github/etc over it. Without --yes, each file is confirmed:' \
            '  y  overwrite this file' \
            '  n  keep the current /etc file' \
            '  a  overwrite this and all remaining files' \
            "  s  keep this and all remaining files" \
            '  q  quit' \
            '' \
            '--yes applies every change without prompting (old behavior).' \
            '--reload also runs the safe reload commands for changed systemd,' \
            'sysctl, journald, and sshd config.'
        return 0
    end

    set -l src_root ~/.github/etc
    if not test -d $src_root
        echo "etc.apply: $src_root does not exist" >&2
        return 1
    end

    set -l interactive yes
    if set -q _flag_yes; or set -q _flag_dry_run
        set interactive no
    else if not test -t 0
        echo 'etc.apply: stdin is not a TTY; rerun with --yes to apply without prompting' >&2
        return 2
    end

    set -l changed
    set -l unchanged 0

    for src in (find $src_root -type f | sort)
        set -l rel (string replace -- "$src_root/" '' $src)
        set -l dest /etc/$rel

        if sudo test -e $dest; and sudo cmp -s -- $src $dest
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

    set -l applied
    set -l skipped 0

    if test $interactive = no
        # Show the old /etc file first so the terminal log records anything that
        # is about to be clobbered.
        for rel in $changed
            set -l src $src_root/$rel
            set -l dest /etc/$rel

            if sudo test -e $dest
                printf '\n~ %s\n' $dest
                sudo diff --unified --color=auto --label $dest --label $src -- $dest $src
            else
                printf '\n+ %s\n' $dest
                diff --unified --color=auto --label /dev/null --label $src -- /dev/null $src
            end
        end

        if set -q _flag_dry_run
            printf '\n%d file(s) would change; nothing written (--dry-run).\n' (count $changed)
            return 0
        end

        set applied $changed
    else
        set -l apply_all no
        set -l skip_all no

        for rel in $changed
            set -l src $src_root/$rel
            set -l dest /etc/$rel

            set -l prompt
            set -l default no
            if sudo test -e $dest
                printf '\n~ %s\n' $dest
                sudo diff --unified --color=auto --label $dest --label $src -- $dest $src
                set prompt "Overwrite $dest with the repo version? [y/N/a/s/q] "
            else
                printf '\n+ %s\n' $dest
                diff --unified --color=auto --label /dev/null --label $src -- /dev/null $src
                set prompt "Create $dest from the repo? [Y/n/a/s/q] "
                set default yes
            end

            set -l choice
            if test $apply_all = yes
                set choice yes
            else if test $skip_all = yes
                set choice no
            else
                while true
                    read -l -P $prompt answer
                    or set answer q
                    set answer (string trim -- (string lower -- "$answer"))

                    switch $answer
                        case y yes
                            set choice yes
                            break
                        case n no
                            set choice no
                            break
                        case ''
                            set choice $default
                            break
                        case a all
                            set apply_all yes
                            set choice yes
                            break
                        case s skip
                            set skip_all yes
                            set choice no
                            break
                        case q quit
                            set choice quit
                            break
                        case '*'
                            printf 'Please answer y, n, a, s, or q.\n'
                    end
                end
            end

            switch $choice
                case yes
                    sudo install -D -m (stat -c %a -- $src) -o root -g root -- $src $dest
                    or return 1
                    if command -q restorecon
                        sudo restorecon -- $dest
                    end
                    set -a applied $rel
                case no
                    set skipped (math $skipped + 1)
                case quit
                    break
            end
        end
    end

    if not set -q applied[1]
        printf 'No files changed; kept %d file(s).\n' $skipped
        return 0
    end

    printf '\nApplied %d file(s)' (count $applied)
    if test $skipped -gt 0
        printf '; kept %d' $skipped
    end
    printf '.\n'

    set -l reloads
    if string match -q 'systemd/*' $applied
        set -a reloads 'sudo systemctl daemon-reload'
    end
    if string match -q 'sysctl.d/*' $applied
        set -a reloads 'sudo sysctl --system'
    end
    if string match -q 'systemd/journald.conf.d/*' $applied
        set -a reloads 'sudo systemctl restart systemd-journald'
    end
    if string match -q 'ssh/sshd_config.d/*' $applied
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

    if string match -q 'systemd/zram-generator.conf.d/*' $applied
        printf '\nzram: size and compression only change when the device is recreated (reboot).\n'
    end
end
