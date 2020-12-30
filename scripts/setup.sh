#!/bin/bash

# This is the universal setup script for FROSTI.  The intent is for this to
# configure both container-land and a stock Raspberry Pi OS instance.  Ideally
# the package lists would be in their own files, but the goal is to enable
# curl'ing this file and execute it stand-alone.

FROSTI_HOME=/usr/local/frosti
FROSTI_STATUS_DIR=/var/spool/frosti
FROSTI_HOSTNAME=pi-frosti-dev

read -r -d '' FROSTI_PACKAGES <<-EOLIST
	curl
	fonts-hack-ttf
	fonts-mplus
	libfreetype6-dev
	libfribidi-dev
	libharfbuzz-dev
	libjpeg-dev
	liblcms2-dev
	libopenjp2-7-dev
	libpq-dev
	libtiff-dev
	libwebp-dev
	libxcb1-dev
	python3
	python3-dev
	python3-pil
	python3-pip
	python3-setuptools
	python3-smbus
	python3-tk
	tcl8.6-dev
	tk8.6-dev
	unzip
	zlib1g-dev
EOLIST


read -r -d '' FROSTI_REQUIREMENTS <<-EOLIST
	Adafruit-Blinka==5.9.1
	adafruit-circuitpython-74hc595==1.2.1
	adafruit-circuitpython-bme280==2.5.1
	adafruit-circuitpython-bmp280==3.2.3
	adafruit-circuitpython-busdevice==5.0.1
	adafruit-circuitpython-charlcd==3.3.4
	adafruit-circuitpython-mcp230xx==2.4.2
	Adafruit-PlatformDetect==2.23.0
	Adafruit-PureIO==1.1.8
	aniso8601==8.1.0
	attrs==20.3.0
	autopep8==1.5.4
	certifi==2020.12.5
	chardet==4.0.0
	click==7.1.2
	flake8==3.8.4
	Flask==1.1.2
	Flask-Cors==3.0.9
	flask-restx==0.2.0
	idna==2.10
	importlib-metadata==3.3.0
	iniconfig==1.1.1
	itsdangerous==1.1.0
	Jinja2==2.11.2
	jsonschema==3.2.0
	MarkupSafe==1.1.1
	mccabe==0.6.1
	packaging==20.8
	Pillow==8.0.1
	pluggy==0.13.1
	psycopg2-binary==2.8.6
	ptvsd==4.3.2
	py==1.10.0
	pycodestyle==2.6.0
	pyflakes==2.2.0
	pyftdi==0.52.0
	pyparsing==2.4.7
	pyrsistent==0.17.3
	pyserial==3.5
	pytest==6.2.1
	pytz==2020.4
	pyusb==1.1.0
	PyYAML==5.3.1
	qrcode==6.1
	requests==2.25.1
	rpi-ws281x==4.2.5
	RPi.GPIO==0.7.0
	six==1.15.0
	spidev==3.5
	SQLAlchemy==1.3.22
	SQLAlchemy-Utils==0.36.8
	sysv-ipc==1.0.1
	toml==0.10.2
	typing-extensions==3.7.4.3
	urllib3==1.26.2
	Werkzeug==1.0.1
	zipp==3.4.0
EOLIST

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
    echo "EXECUTING task '${zz_task}'"
    ${zz_task} || die "Failed task '${zz_task}'"
    mark_completed ${zz_task}
  else
    echo "SKIPPING completed task '${zz_task}'"
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
  sudo apt install -y ${FROSTI_PACKAGES}
  sudo python3 -m pip install ${FROSTI_REQUIREMENTS}
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