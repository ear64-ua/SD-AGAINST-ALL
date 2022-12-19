console.log('Server-side code running');

const express = require('express');
var MongoClient = require('mongodb').MongoClient;
var mongo_url = "mongodb://mongodb";
const app = express();
const cors = require('cors');

app.use(cors({
  origin: '*'
}));

const myArgs = process.argv.slice(2);

// start the express web server listening on 8080
app.listen(8081, () => {
  console.log('🚀 Server running and listening on 8081');
});

app.get('/', (req,res) => {
  console.log('Request received!')
  res.send('hello from api_engine!')
  console.log('Data sent!')
});
 
app.get('/map', (req, res) => {
  console.log('Received GET request')
  var today = new Date();
  var time_ = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var date = today.getFullYear() + '/' + String(today.getMonth() + 1).padStart(2, '0') + '/' + String(today.getDate()).padStart(2, '0');
  time_ = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

  let c1;
  var c2;
  var c3;
  var c4;

  try{
    MongoClient.connect(mongo_url, function(err, db) {
      if (err) throw err;
      else console.log('[DB] connected to MongoDB succesfully !!')

      var dbo = db.db("gameDB");
      var query = { codigoPartida: myArgs[0] };
      dbo.collection("partida").find(query).toArray(function(err, result) {
        if (err) throw err;

        console.log('[0] ',result[0])

        c1 = JSON.parse(result[0]['c1']);
        c2 = JSON.parse(result[0]['c2']);
        c3 = JSON.parse(result[0]['c3']);
        c4 = JSON.parse(result[0]['c4']);
        players = JSON.parse(result[0]['jugadores']);

        db.close();

        var data = [];

        data.push([{casillas: c1['casillas']},{rgb: c1['rgb']}])
        data.push([{casillas: c2['casillas']},{rgb: c2['rgb']}])
        data.push([{casillas: c3['casillas']},{rgb: c3['rgb']}])
        data.push([{casillas: c4['casillas']},{rgb: c4['rgb']}])
        for (player in players){
          data.push(players[player])
        }

        console.log(data)

        res.send(data);
      });
    });
  }catch(e){
    console.log(e)
  }
  console.log('[DB] closed connection')
  
});