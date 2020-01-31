const fs = require('fs');

exports.log = message => {
    data = getDateAndTime() + '|' + message;
    data = new Uint8Array(Buffer.from(data + '\n'));

    fs.appendFile('log.txt', data, err => {
        if (err) throw err;
    });
};

function getDateAndTime() {
    now = new Date();

    day = now.getDay();
    month = now.getMonth() + 1;
    year = now.getFullYear();
    hours = now.getHours();
    minutes = now.getMinutes();
    seconds = now.getSeconds();

    day = day < 10 ? '0' + day : '' + day;
    month = month < 10 ? '0' + month : '' + month;
    hours = hours < 10 ? '0' + hours : '' + hours;
    minutes = minutes < 10 ? '0' + minutes : '' + minutes;
    seconds = seconds < 10 ? '0' + seconds : '' + seconds;

    return `${day}/${month}/${year}|${hours}:${minutes}:${seconds}`;
}
