const mqtt = require('mqtt');

const BROKER = 'mqtt://192.168.0.167';
let client;

let status = [];

exports.connect = () => {
    client = mqtt.connect(BROKER);

    client.on('connect', postConnect);
    client.on('message', gotMessage);
};

exports.getShadesStatus = () => {
    return status.map(item => ({
        netId: item.netId,
        group: item.group,
        state: item.state
    }));
};

function postConnect() {
    client.subscribe('shades/states/#');

    // Remove devices which aren't alive (the ones that didn't send a message since 10 seconds)
    setInterval(_ => {
        const now = new Date().getTime();

        status = status.filter(item => now - item.date.getTime() < 10000);
    }, 1000);
}

function gotMessage(topic, message) {
    if (topic.indexOf('shades/states/') > -1) {
        netId = parseInt(topic.split('shades/states/')[1]);
        jsonMessage = JSON.parse(message.toString());

        status = status.filter(item => item.netId != netId);
        status.push({
            netId,
            group: jsonMessage.group,
            state: jsonMessage.state,
            date: new Date()
        });

        status = status.sort((a, b) => (a.netId < b.netId ? -1 : 1));
    }
}

exports.sendMessage = (topic, message) => {
    client.publish(topic, message);
};
