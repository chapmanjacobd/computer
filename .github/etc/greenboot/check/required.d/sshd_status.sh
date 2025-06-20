#!/bin/bash

function check_sshd_status {
    systemctl is-active --quiet sshd
    if [ $? -eq 0 ]; then
        echo "sshd service is active."
        exit 0
    else
        echo "sshd service is not active."
        exit 1
    fi
}

check_sshd_status
