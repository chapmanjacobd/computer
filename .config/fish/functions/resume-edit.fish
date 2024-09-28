# Defined interactively
function resume-edit
    cd ~/github/o/resume/
    code .
    while inotifywait -e modify inputs/resume.yaml
        python generate.py
    end
end
