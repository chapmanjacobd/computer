#!/usr/bin/env bash

set -Eeuox pipefail

sudo zypper refresh
sudo zypper dist-upgrade --from packman --allow-vendor-change
sudo zypper install --from packman ffmpeg gstreamer-plugins-{good,bad,ugly,libav} libavcodec-full vlc-codecs

sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo zypper addrepo https://packages.microsoft.com/yumrepos/vscode vscode
sudo zypper refresh

sudo zypper install -y mpv python3 python3-pip git android-tools R ImageMagick bat code darktable cowsay dnscrypt-proxy exa evince expect fdupes fish gdal fzf geos-devel  gimp git-delta git-lfs htop inotify-tools jq kdiff3 keepassxc kitty krename lato-fonts libreoffice meld moreutils ncdu nmon nomacs picard podman-docker pspg  python ripgrep rstudio-desktop syncthing udunits2 wine xdotool xclip xbacklight wget  postgresql-devel breeze-gtk gdal-devel sqlite-devel bash-completion krusader xmodmap sysstat poppler-tools ghc-postgresql-libpq socat chromium fd sxhkd xsel gnu_parallel

fisher unnstall sentriz/fish-pipenv
fisher install sentriz/fish-pipenv
fisher uninstall edc/bass
fisher install edc/bass
fisher uninstall fisherman/fzf
fisher install fisherman/fzf
fisher uninstall fisherman/z
fisher install fisherman/z


zypper ar https://download.opensuse.org/repositories/home:/lukho:/copyq/openSUSE_Tumbleweed/home:lukho:copyq.repo

zypper ar https://download.opensuse.org/repositories/Application:/Geo/openSUSE_Tumbleweed/Application:Geo.repo

sudo zypper install copyq qgis

pip3 install trash-cli pipenv tldr yt-dlp

sudo zypper install -y https://zoom.us/client/latest/zoom_openSUSE_x86_64.rpm

sudo zypper install -y https://download2.tixati.com/download/tixati-2.88-1.x86_64.rpm


sudo tee -a /etc/zypp/repos.d/google-cloud-sdk.repo << EOM
[google-cloud-sdk]
name=Google Cloud SDK
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
       https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
sudo zypper ref
sudo zypper in google-cloud-sdk

sudo zypper install -y https://dbeaver.com/files/dbeaver-ee-latest-stable.x86_64.rpm

sudo loginctl enable-linger xk

sudo zypper rm kcalc konversation falkon dragon konversation falkon kget ktorrent konqueror docker autokey kontact dolphin Kontact dolphin kwrite calligra'\*' korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmahjongg kmines kmousetool korganizer kwrite kaddressbook elisa-player

chsh -s /bin/fish

gcloud init
gcloud auth application-default login
gcloud auth login


wget https://download.brother.com/welcome/dlf006893/linux-brprinter-installer-2.2.3-1.gz
unar linux-brprinter-installer-2.2.3-1.gz
sudo bash linux-brprinter-installer-2.2.3-1 HL-L2300D

