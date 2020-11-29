# Upgrading the thermostat

```bash
# Upgrade docker-compose
sudo pip uninstall docker-compose
sudo pip install docker-compose
```

```bash
# Pull the latest images
docker-compose --file docker/docker-compose-arm.yaml pull
```

You may want to backup the database as well

sudo systemctl daemon-reload
/etc/systemd/system/frosti.service
