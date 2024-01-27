# Defined interactively
function dup_word_left_of_cursor
    set -l cmdline (commandline)
    set -l cursor_pos (commandline -C)

    # Move cursor to the end of the current word if inside a word
    set -l end_of_word_pos (string match -r -i '[^ ]*$' -- (string sub -s $cursor_pos -- $cmdline) | string length)
    if test $end_of_word_pos -gt 0
        set cursor_pos (math $cursor_pos + $end_of_word_pos - 0)
    end

    set -l left_part (string sub -l $cursor_pos -- $cmdline)
    set -l right_part (string sub -s (math $cursor_pos + 1) -- $cmdline)

    set -l words_in_left (string split " " -- $left_part)
    set -l last_word

    # Iterate over the words in reverse to find the last non-empty word
    for word in (seq (count $words_in_left) -1 1)
        set -l current_word (string trim -c ' ' -- $words_in_left[$word])
        if test -n "$current_word"
            set last_word $current_word
            break
        end
    end

    # Duplicate the word if found
    if test -n "$last_word"
        commandline -r -- "$left_part $last_word$right_part"
        commandline -C (math $cursor_pos + (string length -- $last_word) + 0)
    end
end
