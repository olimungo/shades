'use strict';

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = require('express')();
const http = require('http').createServer(app);
const tl = require('express-tl');

const mqtt = require('./mqtt');
const websocket = require('./websocket');
const log = require('./logger').log;

const PORT = 8081;

mqtt.connect(mqttMessageReceived);
websocket.createSocket(http, websocketMessageReceived);

app.engine('tl', tl);
app.set('views', './public');
app.set('view engine', 'tl');

app.get('/', (req, res) => {
    res.render('shades', {
        ip: process.env.HOST_IP
    });
});

app.get('*', (req, res) => {
    const file = path.join(__dirname, 'public', req.originalUrl);

    fs.access(file, fs.F_OK, error => {
        if (error) {
            res.sendStatus(404);
        } else {
            res.sendFile(file);
        }
    });
});

http.listen(PORT, _ => console.log(`Running on ${PORT}`));

function websocketMessageReceived(topic, message) {
    mqtt.sendMessage(topic, message);
}

function mqttMessageReceived(type, topic, message, states) {
    switch (type) {
        case 'logs':
            topic = log(`${topic.substr(5)}|${message}`);
            break;
        case 'states':
            websocket.sendMessage(states);
            break;
    }
}
