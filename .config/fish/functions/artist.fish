# Defined interactively
function artist
    python -c "import re, sys; from library.utils import objects, processes; print(objects.value({k:v for d in processes.FFProbe(sys.argv[1]).audio_streams for k,v in d['tags'].items()}, ['artist', 'artists']) or '', end='')"
end
