#!/bin/bash


# This is the universal setup script for FROSTI.  The intent is for this to
# configure both container-land and a stock Raspberry Pi OS instance

FROSTI_HOME=/usr/local/frosti
FROSTI_HOSTNAME=pi-frosti-dev


RPI_STATUS=$(uname -a | grep raspberrypi > /dev/null; echo $?)

if [ "${RPI_STATUS}" = '0' ]; then
    # Setup locale preferences
    sudo raspi-config nonint do_configure_keyboard 'us'
    sudo raspi-config nonint do_change_locale 'en_US.UTF-8'
    sudo raspi-config nonint do_change_timezone 'US/Central'
    sudo raspi-config nonint do_wifi_country 'US'

    # Setup Wifi and hostname
    sudo raspi-config nonint do_hostname 'pi-frosti-dev'

    # Setup the interfaces we want to use
    sudo raspi-config nonint do_spi 1
    sudo raspi-config nonint do_i2c 1
    sudo raspi-config nonint do_ssh 1
    sudo service ssh restart
fi

# Install the core packages we need to get things going
sudo apt update && sudo apt upgrade -y
sudo apt install -y git

# Once things are setup, can now pull down frosti and start configuring
# the environment
mkdir -p ${FROSTI_HOME}
sudo git clone https://github.com/mbtown01/frosti.git ${FROSTI_HOME}
cd ${FROSTI_HOME}
xargs sudo apt install -y < packages.txt
xargs sudo python3 -m pip install < requirements.txt

# Taken from an article at 
# https://withblue.ink/2020/06/24/docker-and-docker-compose-on-raspberry-pi-os.html
# Install some required packages first
sudo apt install -y apt-transport-https ca-certificates curl gnupg2 \
    software-properties-common

# Get the Docker signing key for packages
curl -fsSL \
    https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | \
    sudo apt-key add -

# Add the Docker official repos
echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

# Install Docker
sudo apt update
sudo apt install -y --no-install-recommends docker-ce cgroupfs-mount

# Command line options
for i in $*; do
  case $i in
  --setup=wif)
    OPT_MEMORY_SPLIT=GET
    printf "Not currently supported\n"
    exit 1
    ;;
  --memory-split=*)
    OPT_MEMORY_SPLIT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    printf "Not currently supported\n"
    exit 1
    ;;
  --expand-rootfs)
    INTERACTIVE=False
    do_expand_rootfs
    printf "Please reboot\n"
    exit 0
    ;;
  --apply-os-config)
    INTERACTIVE=False
    do_apply_os_config
    exit $?
    ;;
  nonint)
    INTERACTIVE=False
    "$@"
    exit $?
    ;;
  *)
    # unknown option
    ;;
  esac
done