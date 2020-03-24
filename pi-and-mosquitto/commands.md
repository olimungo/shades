# Setup the Raspberry Pi and Mosquitto

## Burn Raspian to an SD-card

Download and install **Raspberry Pi Imager**: https://www.raspberrypi.org/downloads/

Burn **Raspbian Lite** onto an SD card

To allow a headless config, enable ssh on the Pi. Move to the boot folder on the SD card and create an empty **ssh** file.

on Linux:

```
touch ssh
```

Also, setup your Wifi credentials. Still in the boot folder of the SD card, edit a file called **wpa_supplicant.conf**, add the following content while replacing the **keyword** with your country code and your credentials.

:exclamation: Make sure there is a **TAB** at the start of the lines with **ssid** and **psk**. :exclamation:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=<Insert country code here>

network={
  ssid="<Name of your WiFi>"
  psk="<Password for your WiFi>"
}
```

## Setup the Pi

Insert the SD-card, connect the Pi physically to the Wifi router, boot it, then ssh it with the password **raspberry**

```
ssh pi@rapsberrypi.local
```

### Update the system

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get clean
```

### Configure the Pi

```
sudo raspi-config
```

-   Change the hostname to "nestor"
-   Set locale
-   Set timezone
-   Set keyboard layout

#### Install drivers for the Wifi USB dongle (for Raspberry Pi 2)

```
sudo wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi
```

After installation, reboot the Pi.

## Docker on the Pi

Install docker

```
curl -sSL https://get.docker.com | sh
```

:exclamation: To allow to run docker without sudo apply one of the following solution. :exclamation:

```
sudo usermod -aG docker pi
```

Then, logout from the Pin the login againg to refresh the session.

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
  --name=mosquitto \
  eclipse-mosquitto
```
