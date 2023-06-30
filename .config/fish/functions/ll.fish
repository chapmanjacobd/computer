# Defined via `source`
function ll --wraps='ls -l --color=auto' --description 'alias ll=ls -l --color=auto'
    command ls -l --color=auto $argv

end
