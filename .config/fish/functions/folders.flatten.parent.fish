# Defined interactively
function folders.flatten.parent
    python -c 'from pathlib import Path; from library.utils import shell_utils; [shell_utils.flatten_wrapper_folder(p) for p in Path(".").glob("*") if p.is_dir()]'
end
