function docker.cleanup --description 'Drops unused and temporary images'
    docker rm (docker ps -a -q -f status=exited)
    docker rmi (docker images -q -f dangling=true)
end
