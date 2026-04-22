// var file = '/dev/ttyS0';

// var GPS = require('gps');
// var SerialPort = require('serialport');
// var port = new SerialPort.SerialPort(file, {
//   baudrate: 9600,
//   parser: SerialPort.parsers.readline('\r\n')
// });

// var gps = new GPS;

// gps.on('data', function(data) {
//   console.log(data);
// });

// port.on('data', function(data) {
//   gps.update(data);
// });


// GPT version for updated node.js and serialport package
const SerialPort = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const GPS = require('gps');

// Path to your serial device
const file = '/dev/ttyS0';

// Create serial port connection
const port = new SerialPort.SerialPort({
  path: file,
  baudRate: 9600,
});

// Attach a line-based parser
const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

// Create GPS parser
const gps = new GPS();

// When GPS data is parsed
gps.on('data', data => {
  console.log(data);
});

// Feed each line from serial into the GPS parser
parser.on('data', line => {
  gps.update(line);
});
