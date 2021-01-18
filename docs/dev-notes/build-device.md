# Start a new Raspberry Pi from scratch

## Download the image

Before going anywhere, let's go get the latest version or raspbian from
the Raspberry Pi foundation

[https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)

## Thoughts on an image builder service

- Could host a simple service that builds images, taking a stock image
  and doctoring it just enough to be useful at first boot
- User presented with some simple question/answers
  - WiFi network SSID/password
  - Host and frosti SSH keys
  - Version of FROSTI to start with from github releases/tags
- Using info above, installer would mount the pure Raspberry Pi OS image, and
  boostrap the installer process with the parameters above
  - This may be necessary to create the 3rd read/writeable partition
- This COULD even be a feature of FROSTI, depends on how much space an SD
  card has

## Order operations

- Image builder
  - Gets user input on wifi ssid and password
  - Gets user input on hostname (w/ a default)
  - Creates the intial image
  - Removes the automatic '/' filesystem expansion
  - Adds the startup logic
  - (any other misc update to the base image before first install)
- First startup
  - Configure wireless network
  - Download **core** packages
  - Install FROSTI source
    - Ideally here we'd have enough at this point to start using the CLI to
      give notification to the user that things are happening
      Install the rest of the packages
  - File systems
    - Expand '/' to 3GB
    - Create new '/data' partition
    - Create an in-memory tmpfs for logs and then setup logs to not be
    - so chatty
    - Figure out how to make '/' read-only

## Using Raspbian installer

To setup a new SD card from scratch using Raspbian installer, follow the
following process:

- Burn an image of Raspberry Pi OS "Lite" to an SD card
- Boot the PI and immediately configure your network so ou can talk w/ the
  outside world (this is probably on necessary if you need to use Wifi, a
  wired connection should already just work)

```bash
sudo raspi-config nonint do_wifi_ssid_passphrase 'ssid' 'passphrase'
```

Now just go install stuff...

```bash
curl -fsSL https://raw.githubusercontent.com/mbtown01/frosti/master/scripts/setup.sh | sudo bash -
```

## Using build-image.py

In my example below, I've downloaded and will use
~/Downloads/2020-02-13-raspbian-buster-lite.img as my base image. Notice that
we're using the 'lite' image -- no reason to download a full desktop.

Once downloaded, unzip it to get the actual image out

```bash
unzip ~/Downloads/2020-02-13-raspbian-buster-lite.zip
```

To simplify things, we've built a simple scrip that will take the img file
and tweak it so that the raspberry pi that uses it is immediately bootable.
When it boots, the device _should_ come up on the wireless network and be
open for ssh connections for user 'pi'. The 'pi' account is seeded with the
ssh public key of the user passed to the script.

```bash
sudo ./scripts/build-image.py \
    --image ~/Downloads/2020-02-13-raspbian-buster-lite.img \
    --hostname ${YOUR_HOST_NAME} \
    --user ${LOCAL_USER_WITH_SSH_PUB_KEY} \
    --ssid ${YOUR_SID} \
    --passwd ${YOUR_PASSWD}
```

Now we have an image ready to be placed onto an SD card. There are tons of
resources on-line to show more details about how to do this. The 'lsblk' and
'lsusb' commands can be used to help identify your local SD card device mount.

```bash
sudo dd \
    if=~/Downloads/2020-02-13-raspbian-buster-lite.img \
    of=${YOUR_DEVICE} \
    bs=4M \
    conv=fsync
```

## Configuration

Once the image is booted, it now needs to be configured. Let's ssh in and
take a look around. As the user you specified to the build-image.py script
above, you should now be able to:

```bash
ssh pi@${YOUR_HOST_NAME}
```

We're using Ansible to largely automate the rest of the configuration. To
get there though, we'll have to manually install it

```bash
sudo apt update && sudo apt upgrade -y --fix-missing
sudo apt install -y ansible git i2c-tools vim
```

```bash
cd /usr/local && sudo git clone https://github.com/mbtown01/frosti.git
```

```bash
ansible-playbook etc/ansible.yaml
```

The ansible playbook does the following

- Configures the hardware watchdog to reboot if the CPU locks
- Enables i2c
- Installs docker, docker-compose, and adds use 'pi' to the docker group
- Installs the frosti daemon as a service

Once the play has completed successfully, a reboot is required. If all went
well, at reboot you'll wait a really long time while the Pi downloads and
installs the containers that frosti depends on, then builds the container for
frosti. Once that's complete, it _should_ just magically start.

## Assumptions

Once the device is up and running, we assume it can reach out to the open
internet to download updates and to check Griddy for current electricity
cost information. We also assume it can be reached on the local network
to be seen by client browsers for remote configuration.

## Future work

Should look into running the PI w/o the SD card mounted

https://mtyka.github.io/hardware/2018/10/09/read-only-pi.html#:~:text=One%20work%20around%20is%20to,makes%20it%20way%20less%20likely.
