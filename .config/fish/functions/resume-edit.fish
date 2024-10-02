# Defined interactively
function resume-edit
    cd ~/github/o/resume/
    code .
    while inotifywait -e modify inputs/resume.yaml templates/*/*
        python generate.py
        and cp outputs/jchapman_resume.pdf ~/sync/self/credentials/Jacob_Chapman.pdf
    end
    and with_unli cp ~/sync/self/credentials/Jacob_Chapman.pdf ~/.mnt/web/home/production/admin/public_html/resume.pdf
end
