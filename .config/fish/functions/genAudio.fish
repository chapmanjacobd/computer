function genAudio --argument folder
    cd ~/amp/musicgen/
    ts-node musicgen.ts (filesDeep $folder | fileTypeAudio | shuf -n 40)
    ./run.sh
    ffmpeg -i /tmp/out.ogg (timestamp).ogg
end
