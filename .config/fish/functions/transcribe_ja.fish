# Defined interactively
function transcribe_ja
    whisper_timestamped --accurate --vad auditok -f srt --output_dir (path dirname $argv) --language ja $argv
end
