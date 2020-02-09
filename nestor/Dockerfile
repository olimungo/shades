FROM node:12.14.1-alpine3.11

# Create app directory
WORKDIR /home/node/app

COPY package*.json ./

RUN npm ci --only=production
#RUN npm i

RUN apk add tzdata
RUN ln -s /usr/share/zoneinfo/Europe/Brussels /etc/localtime

# Bundle app source
COPY . .

EXPOSE 8081
CMD [ "npm", "start" ]