'use strict';

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = require('express')();
const http = require('http').createServer(app);
const tl = require('express-tl');

require('./mqtt').connect();
require('./websocket').createSocket(http);

const PORT = 8081;
let hostIp;

// Get the host IP address
exec("/sbin/ip route|awk '/default/ { print $3 }'", (err, stdout, stderr) => {
    if (err) {
        return;
    }

    hostIp = stdout;
});

app.engine('tl', tl);
app.set('views', './public');
app.set('view engine', 'tl');

app.get('/', (req, res) => {
    res.render('shades', {
        ip: hostIp
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
