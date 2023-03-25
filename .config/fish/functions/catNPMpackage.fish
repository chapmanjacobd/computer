function catNPMpackage --argument rguments folder
    fd -tf -S-1mb -E map . $folder -E '*.map' -E '*.d.ts' -E LICENSE -x cat | less -FSRXc
end
