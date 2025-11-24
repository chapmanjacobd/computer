# Defined in /home/xk/.config/fish/functions/mvl.fish @ line 2
function lines.mv --description 'move lines'

    argparse --min-args 2 h/help 's/search=' -- $argv
    or return 1
    set src $argv[1]
    set dest $argv[2]

    if set -q _flag_help
        echo "Move lines of text from one file to another"
        echo "example: lines.mv -s'baz' foo.txt bar.txt"
        return 0
    end

    if set -q _flag_search
        grep -i "$_flag_search" "$src" | tee -a "$dest"
        grep -iv "$_flag_search" "$src" | sponge "$src"
    else
        if confirm "move all lines from $src to $dest (y/N) "
            cat "$src" | tee -a "$dest"
            truncate -s 0 "$src"
        end
    end
end
