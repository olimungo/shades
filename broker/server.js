'use strict';

const path = require('path');
const fs = require('fs');

const app = require('express')();
const http = require('http').createServer(app);

require('./mqtt').connect();
require('./websocket').createSocket(http);

const PORT = 8081;

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/shades.html'));
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
