#!/bin/bash

# This is the universal setup script for FROSTI.  The intent is for this to
# configure both container-land and a stock Raspberry Pi OS instance.  Ideally
# the package lists would be in their own files, but the goal is to enable
# curl'ing this file and execute it stand-alone.

FROSTI_HOME=/usr/local/frosti
FROSTI_STATUS_FILE=/var/cache/frosti-install

OPT_HOSTNAME=''
OPT_SSID=''
OPT_PASSPHRASE=''
OPT_WIFI_COUNTRY='US'
OPT_ROOT_END=3002
OPT_DEVICE=/dev/mmcblk0


read -r -d '' FROSTI_PACKAGES <<-EOLIST
	curl
  dnsmaskq
	fonts-hack-ttf
	fonts-mplus
  hostapd
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
	python3-dev
	python3-pil
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
	Pillow==8.0.1
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
  if [ ! -f "${FROSTI_STATUS_FILE}" ]; then 
    touch "${FROSTI_STATUS_FILE}"
  fi

  if grep -q "^${1}$" "${FROSTI_STATUS_FILE}"; then
    return 1
  else
    return 0
  fi
}

die() {
  echo "${1}"
  exit 1
}

run_and_mark_completed() {
  zz_reboot='NO'
  zz_reboot_flag=''

  for i in $*; do
    case $i in
    --reboot)
      zz_reboot='YES'
      zz_reboot_flag='-r'
      shift
      ;;
    --shutdown)
      zz_reboot='YES'
      zz_reboot_flag='-h'
      shift
      ;;
    *)
      # unknown option
      ;;
    esac
  done  

  zz_task=${1}
  if is_not_completed ${zz_task}; then
    echo "EXECUTING task '${zz_task}'"
    set -x
    "${@}" || die "Failed task '${zz_task}'"
    set +x
    echo "${zz_task}" >> "${FROSTI_STATUS_FILE}"
    if [ 'YES' == "${zz_reboot}" ]; then
      echo "REBOOTING in 5 seconds..."
      sleep 5
      shutdown ${zz_reboot_flag} now
      exit 0
    fi
  else
    echo "SKIPPING completed task '${zz_task}'"
  fi
}

do_setup_wifi() {
  raspi-config nonint do_wifi_country ${OPT_WIFI_COUNTRY}
  raspi-config nonint do_wifi_ssid_passphrase ${OPT_SSID} ${OPT_PASSPHRASE}
}

do_setup_root() {
  parted ${OPT_DEVICE} resizepart 2 ${OPT_ROOT_END} || return 1
  resize2fs "${OPT_DEVICE}p2"
}

do_setup_services() {
  raspi-config nonint do_spi 0
  raspi-config nonint do_i2c 0
  raspi-config nonint do_ssh 0
  systemctl enable ssh || return 1
  service ssh restart || return 1

  # this still somehow does not work need to investigate
  # apt install -y htpdate || return 1
}

do_setup_users() {
  # Create a frosti account
  # Add frosti to docker
  # remove the password on the 'pi' account so only SSH works
  useradd --create-home frosti || return 1
  usermod --groups frosti,i2c,gpio,spi frosti || return 1
  cp -R /home/pi/.ssh /home/frosti || return 1
  chown -R frosti:frosti /home/frosti/.ssh || return 1
  passwd -l pi || return 1
  echo "frosti	ALL=(root) NOPASSWD:/usr/sbin/service" >> /etc/sudoers || return 1

  return 0
}

do_localize_us() {
  raspi-config nonint do_configure_keyboard 'us'
  raspi-config nonint do_change_locale 'en_US.UTF-8'
  locale-gen
  raspi-config nonint do_change_timezone 'US/Central'
}

do_setup_hostname() {
  raspi-config nonint do_hostname ${OPT_HOSTNAME}
}

do_install_packages_core() {
  # Install the core packages we need to get things going
  apt update && apt upgrade -y
  apt update && apt upgrade -y || return 1
  apt install -y git python3 python3-pip || return 1
}

do_install_frosti_source() {
  # Once things are setup, can now pull down frosti and start configuring
  # the environment
  mkdir -pf ${FROSTI_HOME}
  git clone https://github.com/mbtown01/frosti.git ${FROSTI_HOME}
  ln -s /dev/null frosti.log
  chown frosti:frosti -R ${FROSTI_HOME}
  cp /etc/frosti.service /etc/systemd/system
  sudo systemctl enable frosti.service
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
      software-properties-common || return 1

  # Get the Docker signing key for packages
  curl -fsSL \
      https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | \
      apt-key add -

  # Add the Docker official repos
  echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
      $(lsb_release -cs) stable" | \
      tee /etc/apt/sources.list.d/docker.list

  # Install Docker
  apt update || return 1
  apt install -y --no-install-recommends docker-ce cgroupfs-mount libffi-dev || return 1

  # Install Docker Compose from pip (using Python3)
  python3 -m pip install docker-compose || return 1
  usermod --groups docker --append pi || return 1

}

do_setup_hostapd() {
  # Taken from parts of 
  # https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
  cat > /etc/hostapd/hostapd.conf <<EOF
interface=wlan0
ssid=frosti-setup

channel=6
hw_mode=g
macaddr_acl=0
auth_algs=3
ignore_broadcast_ssid=0

wpa=2
wpa_passphrase=frosti-setup
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

  cat > /etc/dnsmasq.conf <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=local# Local wireless DNS domain
address=/frosti.local/192.168.4.1
EOF

  cat >> /etc/dhcpcd.conf <<EOF
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF

  # We don't want these starting unless we say so
  systemctl disable hostapd.service 
  systemctl disable dnsmasq.service
  # Neeeded to do this before I could make anything use wlan0
  rfkill unblock wlan
  # Needed this the first time I ran??
  sudo systemctl unmask hostapd.service
  sudo drtbivr hostapd start

  # Need to figure out how to tell whether we enable the hotspot or if we 
  # connect to the WIFI network at boot...  

}

do_set_readonly_filesystems() {
  # Steps taken from
  # https://medium.com/swlh/make-your-raspberry-pi-file-system-read-only-raspbian-buster-c558694de79

  # Looks like we can take /var/lib and just move it to the rw partition /data
  # or whatever we end up naming it.  We'll still need to move files into 
  # RAM as the article points out, but this will help
  #
  # Before we actually create the RO root, we should snapshot what a base
  # /var/lib looks like so if we have to re-create /data after an fsck fails
  # we can likley do that
  apt remove --purge -y triggerhappy logrotate || return 1
  apt install -y busybox-syslogd || return 1
  apt remove --purge -y rsyslog || return 1

  # Make the file-systems read-only and add the temporary storage
  cat /etc/fstab | \
    sed "s/\(^PARTUUID=.*\)defaults\(.*$\)/\1defaults,ro\2/" \
    > /tmp/fstab
  cp /tmp/fstab /etc/fstab || return 1

  cat >>/etc/fstab <<EOF
tmpfs        /tmp            tmpfs   nosuid,nodev         0       0
tmpfs        /var/log        tmpfs   nosuid,nodev         0       0
tmpfs        /var/tmp        tmpfs   nosuid,nodev         0       0
EOF

  # Move some system files to temp filesystem
  rm -rf /var/lib/dhcp /var/lib/dhcpcd5 /var/spool /etc/resolv.conf || return 1
  ln -s /tmp /var/lib/dhcp || return 1
  ln -s /tmp /var/lib/dhcpcd5 || return 1
  ln -s /tmp /var/spool || return 1
  touch /tmp/dhcpcd.resolv.conf || return 1
  ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf || return 1

  # Update the systemd random seed
  rm /var/lib/systemd/random-seed || return 1
  ln -s /tmp/random-seed /var/lib/systemd/random-seed || return 1

  cat /lib/systemd/system/systemd-random-seed.service | \
    sed "s#\(^Remain.*$\)#\1\nExecStartPre=/bin/echo \"\" >/tmp/random-seed#" \
    > /tmp/seed
  cp /tmp/seed /lib/systemd/system/systemd-random-seed.service || return 1

  PROMPT_COMMAND=set_bash_prompt
  cat >>/home/pi/.bashrc <<EOF
set_bash_prompt() {
    fs_mode=$(mount | sed -n -e "s/^\/dev\/.* on \/ .*(\(r[w|o]\).*/\1/p")
    PS1='\033[01;32m\]\u@\h${fs_mode:+($fs_mode)}\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m \$ '
}

PROMPT_COMMAND=set_bash_prompt
alias remount-ro='sudo mount -o remount,ro /'
alias remount-rw='sudo mount -o remount,rw /'
EOF

}

do_disable_swap() {
  # Must permanently disable swap file before we mess w/ /var
  dphys-swapfile swapoff || return 1
  dphys-swapfile uninstall || return 1
  systemctl disable dphys-swapfile || return 1  
}

do_setup_var() {
  # Create and expand a new /var partition but mount it temporarily so we
  # can populate it first
  parted ${OPT_DEVICE} mkpart primary ext4 ${OPT_ROOT_END} '100%' || return 1
  mkfs.ext4 -F "${OPT_DEVICE}p3" || return 1
  mkdir /var-new || return 1
  mount "${OPT_DEVICE}p3" /var-new || return 1
  # this failed in testing with a file changed, maybe we should repeat this
  # until it works?  Or shutdown all services???
  rsync -avu /var/* /var-new || return 1
  umount /var-new || return 1

  # Backup /var and then restore it into the new mount
  # tar cfzP ${zz_backup} /var  || return 1
  newline="${OPT_DEVICE}p3	 /var  ext4    defaults,noatime  0    1"
  echo ${newline} >> /etc/fstab || return 1
  mount /var || return 1
}

do_build_containers() {
  docker volume create grafana-data || return 1
  docker volume create postgres-data || return 1
  cd /usr/local/frosti || return 1  
  docker-compose --file docker/docker-compose-arm.yaml build grafana || return 1
}

############################################################################
## Start script execution
############################################################################

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
  nonint)
    shift
    "$@"
    exit $?
    ;;
  *)
    # unknown option
    ;;
  esac
done

if is_pi; then

  # Since this is actually where we create the base image, I'm not sure we
  # need to have network credentials here... maybe we should just assume a
  # wired connection so we don't get in the ssid/passphrase business??
  if [ '' != "${OPT_SSID}" -a '' != "${OPT_PASSPHRASE}" ]; then
    run_and_mark_completed do_setup_wifi

    zz_counter=0
    echo "Waiting on wlan0 interface to connect to '${OPT_SSID}'..."
    while [ '1' == $(ifconfig wlan0 | grep -q broadcast; echo $?) ]; do
      zz_counter=$(($zz_counter+1))
      if [ 30 == ${zz_counter} ]; then return 1; fi
      sleep 1
    done
  fi

  if [ '' != "${OPT_HOSTNAME}" ]; then
    run_and_mark_completed do_setup_hostname
  fi

  run_and_mark_completed do_setup_services
  run_and_mark_completed do_setup_users
  run_and_mark_completed do_localize_us
  run_and_mark_completed do_setup_root
fi

run_and_mark_completed do_install_packages_core
run_and_mark_completed do_install_frosti_source
run_and_mark_completed do_install_packages

if is_pi; then
  # At this point, a clean image has been created that can be written to an 
  # IMG file and used later!!  At first boot, this script will continue
  # to the lines after
  run_and_mark_completed --reboot do_install_docker
  
  # At this point, we'll need to expand /var to fill the card since 
  # we've likely started from an image!!
  run_and_mark_completed do_disable_swap
  run_and_mark_completed do_setup_var
  run_and_mark_completed --reboot do_set_readonly_filesystems

  # Do we need to re-connect to the internet now?  We at now use the display
  # so we could throw a link up and have someone connect!  
  run_and_mark_completed do_build_containers
fi


# Thanks for the ASCII art!!
# https://manytools.org/hacker-tools/convert-images-to-ascii-art/go/

zz_hostname=$(ifconfig wlan0 | grep 'inet ' | awk '{ print $2 }')
cat <<EOF

                 @@@@@@@@@@@@@@@@,             @@@@@@@@@@@@@@@@                 
            @@@@@@@@@@@@@@@@@@@@@@@@@@,   @@@@@@@@@@@@@@@@@@@@@@@@@@            
         @@@@@@@                   @@@@@@@@@@@                   @@@@@@.        
       @@@@@                          &@@@                          @@@@@@      
     @@@@@                                                             @@@@%    
    @@@@                                                                @@@@@   
   @@@@                                                                   @@@@  
  @@@@                                                                    &@@@& 
 (@@@#                                                                     @@@@ 
 @@@@                                                                      @@@@ 
 %@@@/                                                                     @@@@ 
  @@@@                                                                    (@@@@ 
  ,@@@@                                                                   @@@@  
   #@@@@                                                                #@@@@   
     @@@@@                                                             @@@@@    
      ,@@@@@                           @@@                          &@@@@@      
         @@@@@@/                   @@@@@@@@@@                    @@@@@@@        
            @@@@@@@@@@@/. ,#@@@@@@@@@@@   @@@@@@@@@@@*. ,&@@@@@@@@@@(           
                 @@@@@@@@@@@@@@@@@            *@@@@@@@@@@@@@@@@@                

FROSTI has been installed successfully!
API CONNECT at http://${zz_hostname}:5000

EOF

if is_pi; then
  ## TODO: How do we start these so they re-start at boot time?  It could
  # be an actual option in the docker-config section for each service 
  # (e.g. restart policy)
  cd /usr/local/frosti || return 1
  docker-compose --file docker/docker-compose-arm.yaml up -d grafana || return 1
  ln -s /dev/null frosti.log
  sudo --user frosti python3 -m frosti
fi


# Disk /dev/mmcblk0: 14.8 GiB, 15833497600 bytes, 30924800 sectors
# Units: sectors of 1 * 512 = 512 bytes
# Sector size (logical/physical): 512 bytes / 512 bytes
# I/O size (minimum/optimal): 512 bytes / 512 bytes
# Disklabel type: dos
# Disk identifier: 0x067e19d7

# Device         Boot   Start      End  Sectors  Size Id Type
# /dev/mmcblk0p1         8192   532479   524288  256M  c W95 FAT32 (LBA)
# /dev/mmcblk0p2       532480  5863281  5330802  2.6G 83 Linux
# /dev/mmcblk0p3      5863424 30924799 25061376   12G 83 Linux

# To backup this image on the Mac based on the partition table above
# - diskutil list  # gets the partition table, look for the SD card!!
# - diskutil unmountDisk /dev/disk2  # Comes up as disk2 for me
# - sudo dd if=/dev/disk2 of=frosti-base.img bs=2862k count=1k

# TODO for a production installation:
#   - Not sure if frosti source needs to actually be owned by frosti??
#   - Setup the watchdog timer, but I think we want OUR software to 'pet'
#     the dog this time and not a service
#   - Setup the actual FROSTI service to run on start-up
#   - Deal with /var failure
#     * A full backup is created right after docker is installed but before
#       any images have been create
#     * Need to check if /var is healthy at reboot and if it isn't, simply
#       blow it away and start a fresh partition and then restore it.  

# /var disk failur 


# TODO for a container/development installation:
#   - Bring in extra packages for developemt time (packages-dev.txt)
#   - Run 