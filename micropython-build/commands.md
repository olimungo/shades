### Create the image

docker build -t -f Dockerfile.base micropython-base .
docker build -t micropython .

### Run container

docker run -d --name=micropython micropython

### Enter the previously created container

docker exec -it micropython /bin/bash -l

### Retrieve firmware

docker cp micropython:/micropython/ports/esp8266/build-GENERIC/firmware-combined.bin ..
