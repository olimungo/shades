# Burn raspian to SD-card
sudo dd bs=1m if=2019-09-26-raspbian-buster-lite.img of=/dev/rdisk3 conv=sync

# Connect it physically to the Wifi router, then ssh it with password "raspberry"
arp -a
ssh pi@192.168.0.xxx

# Change the hostname to "nestor"
# Enable ssh
# Set locale, timezone and keyboard layout
sudo raspi-config

# Install drivers for the Wifi USB dongle
sudo wget http://www.fars-robotics.net/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi

# Config Wifi
# After Wifi config, reboot pi
# Add the following lines to /etc/wpa_supplicant/wpa_supplicant.conf

network={
    ssid="ssid"
    psk="password"
}

# Update
sudo apt-get update
sudo apt-get upgrade
sudo apt-get clean

# MDNS
sudo apt-get install avahi-daemon

# Might be needed... but maybe not...
# To be tested if MDNS is still working without it...
# Maybe ssh with MDNS won't work
sudo apt-get install libnss-mdns

# Make sure that the /etc/nsswitch.conf contains this line:
hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4

# For added convenience, you may want to add the sshd to the advertised services of avahi. Simply add a file /etc/avahi/services/ssh.service containing the following lines:
<?xml version="1.0" standalone='no'?><!--*-nxml-*-->
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">%h</name>
  <service>
     <type>_ssh._tcp</type>
     <port>22</port>
  </service>
</service-group>

# Docker
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh

# or curl -sSL https://get.docker.com | sh

# To allow to run docker without sudo

# Solution 1
# The group should already exists, but in case...
sudo groupadd docker

# Then...
sudo gpasswd -a $USER docker
newgrp docker

# or Solution 2
sudo usermod -aG docker pi

# Docker-compose
sudo apt-get install libffi-dev libssl-dev
sudo apt-get install -y python python-pip
sudo apt-get remove python-configparser
sudo pip install docker-compose

# Mosquitto conf
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_type all

# Mosquitto
docker run -p 1883:1883 -p 9001:9001 -v ~/mosquitto.conf:/home/pi/mosquitto/mosquitto.conf -v ~/log:/home/pi/mosquitto/log -d eclipse-mosquitto

# docker-compose.yaml
version: '3'

services:
  mosquitto:
    image: eclipse-mosquitto
    hostname: mosquitto
    container_name: mosquitto
    expose:
      - "1883"
      - "9001"
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/mosquitto.conf:/home/pi/mosquitto/mosquitto.conf
    networks:
      - default

# Start services
docker-compose up -d

# Download and run container on Pi
docker run -e "HOST_IP=$(ip -4 addr show eth0 | grep -Po 'inet \K[\d.]+')" -p 80:8081 -d --name=nestor olimungo/nestor:1.2