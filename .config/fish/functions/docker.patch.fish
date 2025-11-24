# Defined via `source`
function docker.patch
    docker run -it -v (pwd):/wd $argv[1] /bin/bash

    set container_id (docker ps -aqlf ancestor=$argv[1])
    docker commit $container_id $argv[2]
    docker push $argv[2]
end
