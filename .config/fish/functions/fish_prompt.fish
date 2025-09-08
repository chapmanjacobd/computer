function fish_prompt --description 'Write out the prompt'
    set -l last_status $status
    set -l last_pipestatus $pipestatus
    set -lx __fish_last_status $status # Export for __fish_print_pipestatus.

    if not set -q __fish_git_prompt_show_informative_status
        set -g __fish_git_prompt_show_informative_status 1
    end

    if not set -q __fish_git_prompt_color_branch
        set -g __fish_git_prompt_color_branch magenta --bold
    end
    if not set -q __fish_git_prompt_showupstream
        set -g __fish_git_prompt_showupstream informative
    end
    if not set -q __fish_git_prompt_char_upstream_ahead
        set -g __fish_git_prompt_char_upstream_ahead "↑"
    end
    if not set -q __fish_git_prompt_char_upstream_behind
        set -g __fish_git_prompt_char_upstream_behind "↓"
    end
    if not set -q __fish_git_prompt_char_upstream_prefix
        set -g __fish_git_prompt_char_upstream_prefix ""
    end

    if not set -q __fish_git_prompt_char_stagedstate
        set -g __fish_git_prompt_char_stagedstate "●"
    end
    if not set -q __fish_git_prompt_char_dirtystate
        set -g __fish_git_prompt_char_dirtystate "✚"
    end
    if not set -q __fish_git_prompt_char_untrackedfiles
        set -g __fish_git_prompt_char_untrackedfiles "?"
    end
    if not set -q __fish_git_prompt_char_invalidstate
        set -g __fish_git_prompt_char_invalidstate "✖"
    end
    if not set -q __fish_git_prompt_char_cleanstate
        set -g __fish_git_prompt_char_cleanstate "✔"
    end

    if not set -q __fish_git_prompt_color_dirtystate
        set -g __fish_git_prompt_color_dirtystate blue
    end
    if not set -q __fish_git_prompt_color_stagedstate
        set -g __fish_git_prompt_color_stagedstate yellow
    end
    if not set -q __fish_git_prompt_color_invalidstate
        set -g __fish_git_prompt_color_invalidstate red
    end
    if not set -q __fish_git_prompt_color_untrackedfiles
        set -g __fish_git_prompt_color_untrackedfiles $fish_color_normal
    end
    if not set -q __fish_git_prompt_color_cleanstate
        set -g __fish_git_prompt_color_cleanstate green --bold
    end

    set -l color_host $fish_color_host
    if set -q SSH_TTY
        set color_host $fish_color_host_remote
    end

    if not set -q __fish_prompt_normal
        set -g __fish_prompt_normal (set_color normal)
    end

    set -q VIRTUAL_ENV_DISABLE_PROMPT
    or set -g VIRTUAL_ENV_DISABLE_PROMPT true
    set -q VIRTUAL_ENV
    and set -l venv (echo $VIRTUAL_ENV | md5sum | md5sum | string sub -l 4)

    set -l duration "$cmd_duration$CMD_DURATION"
    if test $duration -gt 300
        set duration (math -s1 $duration / 1000)s
    else
        set duration
    end

    set battery_percentage (low_battery_percent)
    if test -n "$battery_percentage"
        echo -n "$battery_percentage "
    end

    set_color $color_host
    if test -n "$duration"
        printf '%s ' (date '+%H%M')
    else if set -q venv
        printf '(%s) ' $venv
    else if set -q CONTAINER_ID
        printf '(%s) ' $CONTAINER_ID
    else
        printf (rand_block_prefix)
        printf (rand_block_prefix)
        printf (rand_block_prefix)
        printf (rand_block_prefix)
        printf ' '
    end
    set_color normal

    if test -n "$duration"
        printf '%s ' $duration
    end

    set -l color_cwd
    set -l prefix
    set -l suffix
    switch "$USER"
        case root toor
            if set -q fish_color_cwd_root
                set color_cwd $fish_color_cwd_root
            else
                set color_cwd $fish_color_cwd
            end
            # not #️⃣
            set suffix '#'
        case '*'
            set color_cwd $fish_color_cwd
            set suffix (rand_emoji)
    end

    function prompt_git_pwd
        set -q argv[1]
        or set argv (pwd -P)

        set -l reporoot (git rev-parse --show-toplevel 2>/dev/null)
        string replace // / (string replace -r '^'"$reporoot"'($|/)' (basename "$reporoot")':$1/' $argv)
    end

    if string match -q '/net/*' $PWD
        set vcs_prompt ''
    else
        set vcs_prompt (__fish_vcs_prompt)
    end

    # PWD
    set_color $color_cwd
    if test -n "$vcs_prompt"
        echo -n (prompt_git_pwd)
    else
        echo -n (prompt_pwd)
    end
    set_color normal

    printf '%s ' $vcs_prompt

    __fish_print_pipestatus $last_pipestatus

    echo -n "$suffix "
end
