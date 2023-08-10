    if [ -z $3 ] 
    then
        echo "usage: $0 file start_seconds duration [scale=600] [fps=15] [crop]"
        exit 1
    fi

    if [ -z $4 ]
    then
        SCALE=600
    else
        # w=iw/2:h=ih/2 half size
        SCALE="$4"
    fi

    if [ -z $5 ]
    then
        FPS=15
    else
        FPS=$5
    fi

    if [ -z $6 ]
    then 
        CROP="crop=iw:ih:0:0,"
    else
        # CROP="600:ih:250:0" full height
        CROP="setsar=1,crop=${6},"
    fi

    rm "${1}.gif" &> /dev/null

    ffmpeg -ss $2 -t $3 -i "$1" -vf  ${CROP}fps=${FPS},scale=${SCALE}:-1:flags=lanczos,palettegen palette.png -loglevel error
    ffmpeg -ss $2 -t $3 -i "$1" -i palette.png -filter_complex "${CROP}fps=${FPS},scale=${SCALE}:-1:flags=lanczos[x];[x][1:v]paletteuse" "${1}.gif" -loglevel error
