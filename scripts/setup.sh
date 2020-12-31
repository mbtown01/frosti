#!/bin/bash

# This is the universal setup script for FROSTI.  The intent is for this to
# configure both container-land and a stock Raspberry Pi OS instance.  Ideally
# the package lists would be in their own files, but the goal is to enable
# curl'ing this file and execute it stand-alone.

FROSTI_HOME=/usr/local/frosti
FROSTI_STATUS_DIR=/var/spool/frosti

OPT_HOSTNAME=''
OPT_SSID=''
OPT_PASSPHRASE=''
OPT_WIFI_COUNTRY='US'

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
	Adafruit-Blinka
	adafruit-circuitpython-74hc595
	adafruit-circuitpython-bme280
	adafruit-circuitpython-bmp280
	adafruit-circuitpython-busdevice
	adafruit-circuitpython-charlcd
	adafruit-circuitpython-mcp230xx
	Adafruit-PlatformDetect
	Adafruit-PureIO
	aniso8601
	attrs
	autopep8
	certifi
	chardet
	click
	flake8
	Flask
	Flask-Cors
	flask-restx
	idna
	importlib-metadata
	iniconfig
	itsdangerous
	Jinja2
	jsonschema
	MarkupSafe
	mccabe
	packaging
	Pillow
	pluggy
	psycopg2-binary
	ptvsd
	py
	pycodestyle
	pyflakes
	pyftdi
	pyparsing
	pyrsistent
	pyserial
	pytest
	pytz
	pyusb
	PyYAML
	qrcode
	requests
	rpi-ws281x
	RPi.GPIO
	six
	spidev
	SQLAlchemy
	SQLAlchemy-Utils
	sysv-ipc
	toml
	typing-extensions
	urllib3
	Werkzeug
	zipp
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

do_setup_wifi() {
  raspi-config nonint do_wifi_country ${OPT_WIFI_COUNTRY}
  raspi-config nonint do_wifi_ssid_passphrase ${OPT_SSID} ${OPT_PASSPHRASE}
}

do_setup_file_systems() {
  zz_rootsize=4096
  zz_localdev=/dev/mmcblk0
  zz_newdir=/data

  parted ${zz_localdev} resizepart 2 ${zz_rootsize} || return 1
  resize2fs "${zz_localdev}p2"
  parted ${zz_localdev} mkpart primary ext4 ${zz_rootsize} '100%' || return 1
  mkfs.ext4 -F "${zz_localdev}p3" || return 1
  mkdir -p /data || return 1
  newline="${zz_localdev}p3	 ${zz_newdir}   ext4    defaults,noatime  0    1"
  echo ${newline} >> /etc/fstab || return 1
  mount /data || return 1
}

do_setup_services() {
  raspi-config nonint do_spi 0
  raspi-config nonint do_i2c 0
  raspi-config nonint do_ssh 0
  systemctl enable ssh
  service ssh restart
}

do_localize_us() {
  raspi-config nonint do_configure_keyboard 'us'
  raspi-config nonint do_change_locale 'en_US.UTF-8'
  raspi-config nonint do_change_timezone 'US/Central'
}

do_setup_hostname() {
  raspi-config nonint do_hostname ${OPT_HOSTNAME}
}

do_install_packages_core() {
  # Install the core packages we need to get things going
  apt update && apt upgrade -y
  apt update && apt upgrade -y || return 1
  apt install -y git || return 1
}

do_install_frosti_source() {
  # Once things are setup, can now pull down frosti and start configuring
  # the environment
  mkdir -pf ${FROSTI_HOME}
  git clone https://github.com/mbtown01/frosti.git ${FROSTI_HOME}
}

do_install_packages() {
  cd ${FROSTI_HOME}
  apt install -y ${FROSTI_PACKAGES} || return 1
  python3 -m pip install ${FROSTI_REQUIREMENTS} || return 1
}

do_install_docker() {
  # Taken from an article at 
  # https://withblue.ink/2020/06/24/docker-and-docker-compose-on-raspberry-pi-os.html
  # Install some required packages first
  apt install -y apt-transport-https ca-certificates curl gnupg2 \
      software-properties-common

  # Get the Docker signing key for packages
  curl -fsSL \
      https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | \
      apt-key add -

  # Add the Docker official repos
  echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
      $(lsb_release -cs) stable" | \
      tee /etc/apt/sources.list.d/docker.list

  # Install Docker
  apt update
  apt install -y --no-install-recommends docker-ce cgroupfs-mount
}

for i in $*; do
  case $i in
  --wifi_country=*)
    OPT_WIFI_COUNTRY=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
  --ssid=*)
    OPT_SSID=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
  --passphrase=*)
    OPT_PASSPHRASE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
  --hostname=*)
    OPT_HOSTNAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
  --wait=*)
    OPT_WAIT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    sleep ${OPT_WAIT}
    ;;
  *)
    # unknown option
    ;;
  esac
done

if is_pi; then
  if [ '' != "${OPT_SSID}" -a '' != "${OPT_PASSPHRASE}" ]; then
    run_and_mark_completed do_setup_wifi

    # Always wait for the wifi to be active
    zzc=0
    while [ '1' == $(ifconfig wlan0 | grep -q broadcast; echo $?) ]; do
      echo WAITING ON wlan0 $zzc
      zzc=$(($zzc+1))
      if [ 30 == ${zzc} ]; then return 1; fi
      sleep 1
    done
  fi

  if [ '' != "${OPT_HOSTNAME}" ]; then
    run_and_mark_completed do_setup_hostname
  fi

  run_and_mark_completed do_setup_services
  run_and_mark_completed do_localize_us
  run_and_mark_completed do_setup_file_systems
fi

run_and_mark_completed do_install_packages_core
run_and_mark_completed do_install_frosti_source
run_and_mark_completed do_install_packages

if is_pi; then
  run_and_mark_completed do_install_docker
fi

echo SETUP COMPLETE

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
#   - Reset the default pi password

# FOr every boot
#   - Need to fdisk the data volume and check for errors and if they exist
#     maybe we just blow it away and start over??  Need to do some testing
#     with docker on whether that works or not (and )

# TODO for a container/development installation:
#   - Bring in extra packages for developemt time (packages-dev.txt)
#   - Run 