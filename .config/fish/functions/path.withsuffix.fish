function path.withsuffix --description 'Print INPUT with SUFFIX inserted before its extension, optionally replacing the extension' --argument-names input suffix extension
    set -l output_extension (path extension "$input")

    if test -n "$extension"
        set output_extension .(string trim --left --chars . -- "$extension")
    end

    path change-extension "$suffix$output_extension" "$input"
end
