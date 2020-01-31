# Docker

## Development

### Run container on development host and inject the host IP address (macOS)

```bash
sed -e "s/__HOST_IP__/$(ipconfig getifaddr en1)/g" docker-compose.yml | docker-compose --file - up -d
```

### Open a shell in the container

```bash
docker exec -it nestor /bin/bash -l
```

## Build for Raspberry Pi

#### Create builder

```bash
docker buildx create --name nestor-builder
docker buildx use nestor-builder
```

#### Build and push to Docker Hub

```bash
docker buildx build --platform linux/arm/v7 -t olimungo/nestor:1.x --push .
```

#### Download and run container on Pi and inject the host IP address

```bash
docker run -e "HOST_IP=$(ip -4 addr show eth0 | grep -Po 'inet \K[\d.]+')" -p 80:8081 -d --name=nestor olimungo/nestor:1.x
```
