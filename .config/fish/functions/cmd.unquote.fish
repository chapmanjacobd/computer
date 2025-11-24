function cmd.unquote
    if test (count $argv) -eq 0
        python -c "from shlex import join; from ast import literal_eval; import sys; print(join(literal_eval(sys.stdin.read())))"
    else
        python -c "from shlex import join; from ast import literal_eval; import sys; print(join(literal_eval('$argv')))"
        or python -c "from shlex import join; from ast import literal_eval; import sys; print(join(literal_eval('[$argv]')))"
    end
end
