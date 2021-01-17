// Convert a black and white image to binary: https://www.dcode.fr/binary-image
// Make sure that each line of binary data is a multiple of 8 :
//    add "1" or "0" by replacing the regular expression "$" (end of line)
//    by "1"s or "0"s (as many as needed)
//
// Options:
//    - ORIGINAL SIZE
//    - 50% GRAY
//    - BLACK = 0, WHITE = 1

fs = require('fs');

const stream = fs.createReadStream("pepper-clock.binary", {
    encoding: 'utf8',
    fd: null
});

stream.on('readable', function () {
    var chunk;
    var byte = "";
    const hexas = []

    while (null !== (chunk = stream.read(1))) {
        if (chunk == '\n') {
            byte = '';
        } else {
            byte += chunk;

            if (byte.length == 8) {
                hexa = parseInt(byte, 2).toString(16).toUpperCase().padStart(2, '0');
                hexas.push(`\\x${hexa}`);
                byte = '';
            }
        }
    }

    if (hexas.length > 0) {
        console.log(`pepper_clock_icon = bytearray(b\"${hexas.join('')}\")`);
    }
});