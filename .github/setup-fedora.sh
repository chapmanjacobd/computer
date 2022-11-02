#!/usr/bin/env bash

source setup-server.sh

sudo dnf install https://download.nomachine.com/download/7.10/Linux/nomachine_7.10.1_1_x86_64.rpm
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDNOM8a1uNNCgaB0l5qALnACNxFzRZ1Nt9MBfbtrO5/2MkqWYQGGHBcXjIqGqhqTNfQvzFDCKzbaCYEMnE7d/TDyoNh7HhB6XtKi2qsYmDmUWkXfYCzWvRD+/45RiABQcJwJ2Q58fQ4CXeVJWRpdpWjIohOuGJe1diCOSDIurkTw9XqiGwVUU4tLfIdfUCCLYcFTvyz7XBL6LIvLkokxKD0FkDJvijxKVk0R0EMjYmoaVAQXblFDQhM0wg5urYo8Oz3pnPoSd/rTb35yy1e9Zrw3GqebV1q5pMolqz77gslZait/c0zq1xdS2TH7KNK8z0EQtM6LQ99TZPOwKtHGwTqCr/GM8cgJlNCCmwilPtX6fz3rSFhmw9MXZACVwUTVoONIc1cRcCoZr/rmDea4Ai1nYBslLsDFaLBFjR2rdFoDHpsND8ELX7KROh+4QZOxI6nfu3zw/xS5eLkMnF1I+9sTlclr03xPv5idCOX6PappCeSyKBN4PmvGQEeV8yWwU0=" > ~/.nx/config/authorized.crt
chmod 0600 ~/.nx/config/authorized.crt
echo "EnableUPnP none" | sudo tee -a /usr/NX/etc/server.cfg
echo "NXKeyBasedUsePAM 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "AcceptedAuthenticationMethods NX-private-key" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableAdministratorLogin 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableNetworkBroadcast 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableSyslogSupport 1" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableWebPlayer 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableDiskSharing none" | sudo tee -a /usr/NX/etc/node.cfg
echo "EnablePublicDiskSharing 0" | sudo tee -a /usr/NX/etc/node.cfg
echo "EnableSyslogSupport 1" | sudo tee -a /usr/NX/etc/node.cfg
sudo /usr/NX/bin/nxserver --restart

echo "sshfs#xk@bababushka.duckdns.org:/mnt/d/	  /mnt/d	fuse   defaults,user,nofail,_netdev,reconnect,delay_connect,ConnectTimeout=5,ServerAliveInterval=5,TCPKeepAlive=no,port=564 0 0" | sudo tee -a /etc/fstab

sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf group update core -y
sudo dnf --with-optional -y groupinstall Multimedia
sudo dnf install -y gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel
sudo dnf install -y lame\* --exclude=lame-devel

sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'

sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-sdk]
name=Google Cloud SDK
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el8-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
       https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM

sudo rpmkeys --import https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg
printf "[gitlab.com_paulcarroty_vscodium_repo]\nname=download.vscodium.com\nbaseurl=https://download.vscodium.com/rpms/\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=1\ngpgkey=https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg\nmetadata_expire=1h" | sudo tee -a /etc/yum.repos.d/vscodium.repo

sudo dnf install -y codium google-cloud-sdk mpv ffmpeg python3 python3-pip git android-tools R ImageMagick bat code copyq darktable java-latest-openjdk detox cowsay dnscrypt-proxy exa evince expect fdk-aac fdupes fish gdal fzf gdal-devel ffmpeg-devel gdal-java geos-devel gdal-python-tools gimp git-delta git-lfs htop inotify-tools jq kdiff3 keepassxc kitty krename lato-fonts libpq-devel libreoffice mediawriter meld moreutils ncdu nmon nomacs pdfmod pg_top picard plasma-workspace-x11 podman-docker pspg python3-qgis python3.8 ripgrep rstudio-desktop syncthing udunits2 wine xdotool xclip xbacklight trash-cli tldr wget fedora-workstation-repositories chromium-freeworld dnf-plugins-extras-tracer cpufrequtils postgresql-devel breeze-gtk gdal-devel sqlite-devel bash-completion fd-find krusader xmodmap sxhkd xsel xinput kcron parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance ddcutil dnf-automatic xset rmlint skanpage mpv-mpris

#setxkbmap us -variant altgr-intl -option caps:backspace

wget https://github.com/tom-james-watson/breaktimer-app/releases/latest/download/BreakTimer.AppImage -P ~/.local/bin/

sudo dnf install -y https://zoom.us/client/latest/zoom_x86_64.rpm
sudo dnf install -y https://download2.tixati.com/download/tixati-2.89-1.x86_64.rpm
sudo dnf install -y https://dbeaver.io/files/dbeaver-ce-latest-stable.x86_64.rpm

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror chromium docker autokey kontact dolphin Kontact dolphin kwrite calligra* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmahjongg kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring
# sudo dnf erase plasma-discover

#gcloud init
#gcloud auth application-default login
#gcloud auth login
#https://www.ctrl.blog/entry/fedora-hibernate.html
python -m pip install --upgrade pip
python -m pip install yt-dlp pipenv catt

#rsync -ah --info=progress2 --no-inc-recursive /run/media/xk/backup/xk/ ~/
#cd ~ && restorecon -vR .
#reboot
