# Defined interactively
function pdfsmall_grey
    gs -q -dNOPAUSE -dBATCH -dSAFER -sProcessColorModel=DeviceGray -sColorConversionStrategy=Gray -dDownsampleColorImages=true -dOverrideICC -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dColorImageDownsampleType=/Bicubic -dColorImageResolution=120 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=120 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=120 -sOutputFile=out.pdf $argv
end
