function skipthrough
    while fish -c "echo 'no-osd seek 5' | socat - $MPV_SOCKET"
        and :
        and sleep 2
    end

    trash $MPV_SOCKET
end
