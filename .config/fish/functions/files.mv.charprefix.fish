# Defined interactively
function files.mv.charprefix
    # before resorting to something like this, try exiftool:
    # exiftool '-Filename<${Artist;}/' -ext .opus .

    mkdir (seq.alpha A Z) nonalpha

    for p in (fd -tf --exact-depth 1 . $argv)
        set first_char (string sub --length 1 "$p")

        if string match --quiet --regex '[a-zA-Z]' -- "$first_char"
            set target_dir (string upper "$first_char")
        else
            set target_dir nonalpha
        end

        mv "$p" "$target_dir/"
    end
end
