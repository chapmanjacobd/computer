#!/usr/bin/env bash

set -Eeuox pipefail

#source "${BASH_SOURCE%/setup-server.sh}"
sudo systemctl set-default graphical.target

chmod 0600 ~/.nx/config/authorized.crt
echo "EnableUPnP none" | sudo tee -a /usr/NX/etc/server.cfg
echo "NXKeyBasedUsePAM 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "AcceptedAuthenticationMethods NX-private-key" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableAdministratorLogin 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableNetworkBroadcast 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableSyslogSupport 1" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableWebPlayer 0" | sudo tee -a /usr/NX/etc/server.cfg
echo "AuthorizationTimeout 100" | sudo tee -a /usr/NX/etc/server.cfg
echo "EnableDiskSharing none" | sudo tee -a /usr/NX/etc/node.cfg
echo "EnablePublicDiskSharing 0" | sudo tee -a /usr/NX/etc/node.cfg
echo "EnableSyslogSupport 1" | sudo tee -a /usr/NX/etc/node.cfg
echo "UpdateFrequency 0" | sudo tee -a /usr/NX/etc/node.cfg
sudo /usr/NX/bin/nxserver --restart

sudo rm /etc/xdg/plasma-workspace/env/nx-sourceenv.sh

sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf group update core -y
sudo dnf --with-optional -y groupinstall Multimedia
sudo dnf install -y gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel
sudo dnf install -y lame\* --exclude=lame-devel

sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'

cat .github/vscode_extensions.txt | xargs -I{} -n1 code --install-extension {} --force

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

sudo dnf copr enable cboxdoerfer/fsearch

sudo dnf update
sudo dnf install -y codium google-cloud-sdk mpv ffmpeg python3 python3-pip git android-tools R ImageMagick bat code copyq darktable java-latest-openjdk detox cowsay dnscrypt-proxy exa evince expect fdk-aac fdupes fish gdal fzf gdal-devel ffmpeg-devel gdal-java geos-devel gdal-python-tools gimp git-delta git-lfs htop inotify-tools jq kdiff3 keepassxc kitty krename lato-fonts libpq-devel libreoffice mediawriter meld moreutils ncdu nmon nomacs pdfmod pg_top picard plasma-workspace-x11 podman-docker pspg python3-qgis python3.8 ripgrep rstudio-desktop syncthing udunits2 wine xdotool xclip xbacklight trash-cli tldr wget fedora-workstation-repositories dnf-plugins-extras-tracer cpufrequtils postgresql-devel breeze-gtk gdal-devel sqlite-devel bash-completion fd-find krusader xmodmap sxhkd xsel xinput kcron parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance ddcutil dnf-automatic xset rmlint skanpage mpv-mpris code fsearch

#setxkbmap us -variant altgr-intl -option caps:backspace

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror docker autokey kontact dolphin Kontact dolphin kwrite calligra* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring
# sudo dnf erase plasma-discover

#gcloud init
#gcloud auth application-default login
#gcloud auth login
#https://www.ctrl.blog/entry/fedora-hibernate.html
# sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target

python -m ensurepip
python -m pip install --upgrade pip
for dep in $(cat .github/pip_installed); do
    python -m pip install $dep
done
python -m pip install yt-dlp pipenv catt xklb

#rsync -ah --info=progress2 --no-inc-recursive /run/media/xk/backup/xk/ ~/
cd ~ && restorecon -vR .
#reboot
R --slave -e 'update.packages()'
