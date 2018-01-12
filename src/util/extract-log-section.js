const fs = require('fs');
const readline = require('readline');
const lineReader = readline.createInterface({input: process.stdin, output: process.stdout, terminal: false});
const pattern = process.argv[2];
const beforePattern = new RegExp('\\{' + pattern);
const afterPattern = new RegExp(pattern + '\\}');
let insideMatch = false;

lineReader.on('line', line => {
	if(beforePattern.test(line)) insideMatch = true;
	if(insideMatch) console.log(line.replace(/\s*\+\d+:/, ''));
	if(afterPattern.test(line)) insideMatch = false;
});
