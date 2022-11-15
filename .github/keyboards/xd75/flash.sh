#!/bin/sh
qmk compile ~/.github/keyboards/xd75/xk.json
qmk flash ~/bin/qmk/.build/xiudi_xd75_xk.hex
