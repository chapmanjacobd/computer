# Defined interactively
function un_paragraph
    python -c "from library.utils import strings; import sys; print(strings.un_paragraph(sys.stdin.read()))"
end
