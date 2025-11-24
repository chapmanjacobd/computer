# Defined interactively
function lines.unparagraph
    python -c "from library.utils import strings; import sys; print(strings.un_paragraph(sys.stdin.read()))"
end
