# Defined interactively
function pdf.shrink --wraps='gs'
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH -sOutputFile=(path.new "$argv") $argv
end
