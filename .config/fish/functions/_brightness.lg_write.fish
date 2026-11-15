function _brightness.lg_write --argument-names value
    sudo modprobe i2c-dev; and until.n 5 sudo ddcutil setvcp --mfg GSM 10 (math min 100,(math max 1,$value))
end
