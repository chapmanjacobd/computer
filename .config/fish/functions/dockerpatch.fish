# Defined interactively
function dockerpatch
    docker run -it -v (pwd):/pwd $argv[1] /bin/bash

    set container_id (docker container ls -lq)
    docker commit $container_id $argv[2]
    docker push $argv[2]
end
