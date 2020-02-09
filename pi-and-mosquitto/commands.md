# Setup the Raspberry Pi and Mosquitto

## Burn Raspian to an SD-card (MacOS)

```
sudo dd bs=1m if=2019-09-26-raspbian-buster-lite.img of=/dev/rdiskx conv=sync
```

## Configure the Pi

Insert the SD-card, connect the Pi physically to the Wifi router, boot it, then ssh it with the password **raspberry**

### Setup with raspi-config

```
arp -a
ssh pi@192.168.0.xxx
sudo raspi-config
```

-   Change the hostname to "nestor"
-   Enable ssh
-   Set locale
-   Set timezone
-   Set keyboard layout

#### Install drivers for the Wifi USB dongle

```
sudo wget http://www.fars-robotics.net/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi
```

After installation, reboot the Pi and add the following lines to /etc/**wpa_supplicant/wpa_supplicant.conf**

```
network={
  ssid="ssid"
  psk="password"
}
```

Update the system

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get clean
```

### Install MDNS

```
sudo apt-get install avahi-daemon
```

Might be needed... but maybe not... to be tested if MDNS is still working without it... Maybe ssh with MDNS won't work ! #TODO #CHECK

```
sudo apt-get install libnss-mdns
```

Make sure that the /etc/nsswitch.conf contains this line:

```
hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4
```

For added convenience, you may want to add the sshd to the advertised services of avahi. Simply add a file /etc/avahi/services/ssh.service containing the following lines:

```
<?xml version="1.0" standalone='no'?><!--*-nxml-*-->
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">%h</name>
  <service>
     <type>_ssh._tcp</type>
     <port>22</port>
  </service>
</service-group>
```

## Docker on the Pi

Install docker

```
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
```

or

```
curl -sSL https://get.docker.com | sh
```

:exclamation: To allow to run docker without sudo apply one of the following solution.

#### Solution 1

The group should already exists, but in case...

```
sudo groupadd docker
```

Then...

```
sudo gpasswd -a \$USER docker
newgrp docker
```

#### or Solution 2

```
sudo usermod -aG docker pi
```

## Mosquitto

mosquitto.conf

```
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_type all
```

### Run it

```

docker run \
  -p 1883:1883 \
  -p 9001:9001 \
  -v ~/mosquitto.conf:/home/pi/mosquitto/mosquitto.conf \
  -v ~/log:/home/pi/mosquitto/log \
  -d \
  eclipse-mosquitto
```
