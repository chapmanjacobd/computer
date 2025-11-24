function mpv.seek.random
    while fish -c "echo 'no-osd seek '(random 1 40) | socat - $MPV_SOCKET"
        and :
        and sleep 2
    end

    trash $MPV_SOCKET
end
