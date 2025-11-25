# Defined interactively
function resume.edit
    cd ~/github/o/resume/
    code .

    open outputs/jchapman_resume.pdf
    while inotifywait -e modify inputs/resume.yaml templates/*/*
        python generate.py
        gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$HOME/sync/self/credentials/Jacob_Chapman.pdf" ~/github/o/resume/outputs/jchapman_resume.pdf
        with.unli cp ~/sync/self/credentials/Jacob_Chapman.pdf /net/web/var/www/unli.xyz/resume.pdf
    end
end
