const socketIo = require('socket.io');
const mqtt = require('./mqtt');

let io;
let sockets = [];

exports.createSocket = http => {
    io = socketIo(http);
    io.on('connection', connected);
};

function connected(socket) {
    sockets.push(socket);

    socket.on('mqtt-command', message => {
        command = JSON.parse(message);

        command.netIds.forEach(netId => {
            mqtt.sendMessage(`${command.topic}/${netId}`, command.message);
        });
    });

    setInterval(_ => {
        io.emit('update', {
            shades: mqtt.getShadesStatus()
        });
    }, 1000);
}
