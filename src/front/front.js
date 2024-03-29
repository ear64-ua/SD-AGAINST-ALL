const express = require('express');
const app = express();
const cors = require('cors');

app.use(cors({
  origin: '*'
}));

// serve files from the public directory
app.use(express.static('public'));

// start the express web server listening on 8080
app.listen(8080, () => {
  console.log('listening on 8080');
});

// serve the homepage
app.get('/', (req, res) => {
  res.sendFile(__dirname + 'public/index.html');
});