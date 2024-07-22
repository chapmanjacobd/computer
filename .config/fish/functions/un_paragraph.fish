# Defined interactively
function un_paragraph
    python -c "from xklb.utils import strings; import sys; print(strings.un_paragraph(sys.stdin.read()))"
end
