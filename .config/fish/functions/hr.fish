function hr --description 'Print a horizontal rule across the terminal'
    argparse --name hr 'w/width=' 'c/char=' -- $argv
    or return

    set -l char ─
    if set -q _flag_char
        set char $_flag_char
    end
    if test (string length -- $char) -ne 1
        echo "hr: --char must be a single character" >&2
        return 1
    end

    set -l width
    if set -q _flag_width
        set width $_flag_width
        if not string match -qr '^[0-9]+$' -- $width; or test $width -le 0
            echo "hr: --width must be a positive integer" >&2
            return 1
        end
    else
        set width (tput cols 2>/dev/null | string match -r '^[0-9]+$')
        test -n "$width"; or set width 80
    end

    set -l label (string join ' ' -- $argv | string trim)
    if test -z "$label"
        string repeat -n $width -- $char
        return
    end

    set -l text " $label "
    set -l fill (math $width - (string length -- $text))
    if test $fill -lt 2
        printf '%s\n' $label
        return
    end

    set -l left (math "floor($fill / 2)")
    set -l right (math $fill - $left)
    printf '%s%s%s\n' (string repeat -n $left -- $char) $text (string repeat -n $right -- $char)
end
