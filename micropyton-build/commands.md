### Create the image

docker build -t micropython .

### Run container

docker run -d --name=micropython micropython

### Enter the previously created container

docker exec -it micropython /bin/bash -l

### Copy slimDNS.py

docker cp slimDNS.py micropython:/micropython/ports/esp8266/modules

### Retrieve firmware

docker cp micropython:/micropython/ports/esp8266/build-GENERIC/firmware-combined.bin ..
