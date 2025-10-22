#!/bin/bash

# Exit script as soon as a command fails.
set -o errexit

RESOLV_CONF=/etc/resolv.conf
DNSCRYPT_RESOLV=/etc/resolv.conf.dnscryptBackup

sudo cp $RESOLV_CONF $DNSCRYPT_RESOLV
sudo chattr -i $RESOLV_CONF
sudo rm -f $RESOLV_CONF
echo "Restarting the NetworkManager"
sudo systemctl restart NetworkManager
echo "Wait for the connection"
echo "Then, login to the captive portal"

while true
do
    read -p "Did you login?(Y/N) " answer
    case $answer in
        [yY]* ) sudo rm -f $RESOLV_CONF
                sudo cp $DNSCRYPT_RESOLV $RESOLV_CONF
                sudo rm -f $DNSCRYPT_RESOLV
                sudo chattr +i $RESOLV_CONF
                echo "Final nameservers:"
                cat $RESOLV_CONF
                echo "Restarting dnscrypt-proxy..."
                sudo systemctl restart dnscrypt-proxy
                echo "Done"
                break;;

        [nN]* ) exit;;

        * )     echo "Enter Y or N, please.";;
    esac
done
