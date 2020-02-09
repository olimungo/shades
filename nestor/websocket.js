const socketIo = require('socket.io');

let io;

exports.createSocket = (
    http,
    callbackCommandReceived,
    callbackGetStatesReveived
) => {
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

        socket.on('get-states', _ => {
            callbackGetStatesReveived();
        });
    });
};

exports.sendMessage = states => {
    io.emit('update', {
        shades: states
    });
};
