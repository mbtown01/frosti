# Start a new Raspberry Pi from scratch

## Download the image

Before going anywhere, let's go get the latest version or raspbian from
the Raspberry Pi foundation

[https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)

## Using build-image.py

In my example below, I've downloaded and will use
~/Downloads/2020-02-13-raspbian-buster-lite.img as my base image.  Notice that
we're using the 'lite' image -- no reason to download a full desktop.

Once downloaded, unzip it to get the actual image out

```bash
unzip ~/Downloads/2020-02-13-raspbian-buster-lite.zip
```

To simplify things, we've built a simple scrip that will take the img file
and tweak it so that the raspberry pi that uses it is immediately bootable.
When it boots, the device *should* come up on the wireless network and be
open for ssh connections for user 'pi'.  The 'pi' account is seeded with the
ssh public key of the user passed to the script.

```bash
sudo ./scripts/build-image.py \
    --image ~/Downloads/2020-02-13-raspbian-buster-lite.img \
    --hostname ${YOUR_HOST_NAME} \
    --user ${LOCAL_USER_WITH_SSH_PUB_KEY} \
    --ssid ${YOUR_SID} \
    --passwd ${YOUR_PASSWD}
```

Now we have an image ready to be placed onto an SD card.  There are tons of
resources on-line to show more details about how to do this.  The 'lsblk' and
'lsusb' commands can be used to help identify your local SD card device mount.

```bash
sudo dd \
    if=~/Downloads/2020-02-13-raspbian-buster-lite.img \
    of=${YOUR_DEVICE} \
    bs=4M \
    conv=fsync
```

## Configuration

Once the image is booted, it now needs to be configured.  Let's ssh in and
take a look around.  As the user you specified to the build-image.py script
above, you should now be able to:

```bash
ssh pi@${YOUR_HOST_NAME}
```

We're using Ansible to largely automate the rest of the configuration.  To
get there though, we'll have to manually install it

```bash
sudo apt update && sudo apt upgrade -y --fix-missing
sudo apt install -y ansible git i2c-tools vim
```

```bash
cd /usr/local && sudo git clone https://github.com/mbtown01/rpt.git
```

```bash
ansible-playbook etc/ansible.yaml
```

The ansible playbook does the following

* Configures the hardware watchdog to reboot if the CPU locks
* Enables i2c
* Installs docker, docker-compose, and adds use 'pi' to the docker group
* Installs the rpt daemon as a service

Once the play has completed successfully, a reboot is required.  If all went
well, at reboot you'll wait a really long time while the Pi downloads and
installs the containers that rpt depends on, then builds the container for
rpt.  Once that's complete, it *should* just magically start.

## Assumptions

Once the device is up and running, we assume it can reach out to the open
internet to download updates and to check Griddy for current electricity
cost information.  We also assume it can be reached on the local network
to be seen by client browsers for remote configuration.

## Future work

Should look into running the PI w/o the SD card mounted

https://mtyka.github.io/hardware/2018/10/09/read-only-pi.html#:~:text=One%20work%20around%20is%20to,makes%20it%20way%20less%20likely.