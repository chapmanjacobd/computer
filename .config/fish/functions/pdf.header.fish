# Defined via `source`
function pdf.header
    pandoc -V pagestyle=empty -V geometry:paperwidth=21.6cm -V geometry:paperheight=28cm -V geometry:margin=0.3cm (print "\\hfill $argv" | psub -s txt) -o header.pdf
    echo pdftk input.pdf stamp header.pdf output print.pdf
end
