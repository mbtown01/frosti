#!/bin/bash


# This is the universal setup script for FROSTI.  The intent is for this to
# configure both container-land and a stock Raspberry Pi OS instance

FROSTI_HOME=/usr/local/frosti
FROSTI_STATUS_DIR=/var/spool/frosti
FROSTI_HOSTNAME=pi-frosti-dev

is_pi () {
  # Taken directly from raspi-config
  ARCH=$(dpkg --print-architecture)
  if [ "$ARCH" = "armhf" ] || [ "$ARCH" = "arm64" ] ; then
    return 0
  else
    return 1
  fi
}

is_not_completed() {
  # Returns 0 if the task has been completed, 1 otherwise which is only
  # reasonable because we're using it in shell logic
  if [ ! -d "${FROSTI_STATUS_DIR}" ]; then 
    mkdir -p "${FROSTI_STATUS_DIR}"
  fi

  if [ ! -f "${FROSTI_STATUS_DIR}/setup_status" ]; then 
    touch "${FROSTI_STATUS_DIR}/setup_status"
  fi

  if grep -q "^${1}$" "${FROSTI_STATUS_DIR}/setup_status"; then
    return 1
  else
    return 0
  fi
}

mark_completed() {
  echo "${1}" >> "${FROSTI_STATUS_DIR}/setup_status"
}

die() {
  echo "${1}"
  exit 1
}

run_and_mark_completed() {
  zz_task=${1}

  if is_not_completed ${zz_task}; then
    ${zz_task} || die "Failed task '${zz_task}'"
    mark_completed ${zz_task}
  else
    echo "Skipping completed task '${zz_task}'"
  fi
}

do_localize_us() {
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
}

do_install_packages_core() {
  # Install the core packages we need to get things going
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y git
}

do_install_frosti_source() {
  # Once things are setup, can now pull down frosti and start configuring
  # the environment
  mkdir -p ${FROSTI_HOME}
  sudo git clone https://github.com/mbtown01/frosti.git ${FROSTI_HOME}
}

do_install_packages() {
  cd ${FROSTI_HOME}
  xargs sudo apt install -y < packages.txt
  xargs sudo python3 -m pip install < requirements.txt
}

do_install_docker() {
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
}

run_and_mark_completed do_install_packages_core
run_and_mark_completed do_install_frosti_source
run_and_mark_completed do_install_packages

if is_pi; then
  run_and_mark_completed do_localize_us
  run_and_mark_completed do_install_docker
fi

# TODO for a production installation:
#   - Setup the watchdog timer, but I think we want OUR software to 'pet'
#     the dog this time and not a service
#   - Add a frosti/frosti user/group and give it docker access and enough
#     sudo access to reboot and do some simple network config
#   - Setup the actual FROSTI service to run on start-up
#   - Create a 2nd partition to store docker volumes on
#   - Setup / as 'read-only' (think we need a 'lock.sh' and 'unlock.sh' here)
#   - Move /var to a tmpfs and update the log intervals (I've seen this 
#     somewhere before, didn't look too hard!)
#   - Add an option to let the installation script configure the wifi
#     credentials, but we still need to suppor the creation of a temporary
#     local SSID to accept config changes

# TODO for a container/development installation:
#   - Bring in extra packages for developemt time (packages-dev.txt)
#   - Run 

# Command line options
# for i in $*; do
#   case $i in
#   --setup=wif)
#     OPT_MEMORY_SPLIT=GET
#     printf "Not currently supported\n"
#     exit 1
#     ;;
#   --memory-split=*)
#     OPT_MEMORY_SPLIT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
#     printf "Not currently supported\n"
#     exit 1
#     ;;
#   --expand-rootfs)
#     INTERACTIVE=False
#     do_expand_rootfs
#     printf "Please reboot\n"
#     exit 0
#     ;;
#   --apply-os-config)
#     INTERACTIVE=False
#     do_apply_os_config
#     exit $?
#     ;;
#   nonint)
#     INTERACTIVE=False
#     "$@"
#     exit $?
#     ;;
#   *)
#     # unknown option
#     ;;
#   esac
# done