# Defined interactively
function dockercp
    docker compose -f docker/docker-compose.yaml cp (docker compose -f docker/docker-compose.yaml ls | tail -1 | cut -f1 -d' '):$argv .
end
