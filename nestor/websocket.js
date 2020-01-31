const socketIo = require('socket.io');

let io;

exports.createSocket = (http, callbackCommandReceived) => {
    io = socketIo(http);

    io.on('connection', socket => {
        socket.on('mqtt-command', message => {
            command = JSON.parse(message);

            command.netIds.forEach(netId => {
                callbackCommandReceived(
                    `${command.topic}/${netId}`,
                    command.message
                );
            });
        });
    });
};

exports.sendMessage = status => {
    io.emit('update', {
        shades: status
    });
};
