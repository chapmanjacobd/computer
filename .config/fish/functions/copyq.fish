# Defined interactively
function copyq
    if isatty 1
        command copyq $argv
    else if test (count $argv) -eq 0
        command copyq eval '
            for (var i = 0; i < size(); ++i) {
                print(str(read(i)) + "\n\n");
            }
        '
    else
        command copyq $argv
    end
end
