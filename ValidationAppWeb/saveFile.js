const fs = require('fs');
fs.writeFile('resources/test.csv', aux, err => {
    if (err) {
        console.error(err);
    }
    // file written successfully
});