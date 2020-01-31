FROM node:12

# Create app directory
WORKDIR /home/node/app

COPY package*.json ./

RUN npm ci --only=production
#RUN npm i

# Bundle app source
COPY . .

EXPOSE 8081
CMD [ "npm", "start" ]