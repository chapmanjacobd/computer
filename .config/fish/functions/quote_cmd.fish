function quote_cmd
    if test (count $argv) -eq 0
        python -c "from shlex import split; import sys; print(split(sys.stdin.read()))"
    else
        python -c "from shlex import split; import sys; print(split('$argv'))"
    end
end
