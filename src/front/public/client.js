
console.log('Client-side code running');

(function() {
  setInterval(function() {

    // setInterval se encargara de manera asincrona de llamarse cada segundo
    
    // mandamos la peticion GET de html
    try{
      const err = document.querySelector('.error');
      err.style.display = 'none'
      var req = new XMLHttpRequest();
      console.log('Sending request ');
      req.open( "GET", "http://localhost:8081/map", false ); // false for synchronous request
      req.send( null );

      var json = JSON.parse(req.responseText);
      console.log(json);

      // pillamos los elementos html que coinciden con la clase que tiene como nombre city
      var city_div = document.getElementsByClassName('city');

      // iteramos sobre las 4 ciudades
      for (let i = 0; i < 4; i++){

          city_content = "";
          
          // iteramos sobre las 10 filas
          for (let k = 0; k < 10; k++){
              // iteramos sobre las 10 columnas
              for (let j = 0; j < 10; j++){
                  if (json[i][0]['casillas'][k][j] == ".")
                      city_content = city_content + "   .   ";
                  else if (json[i][0]['casillas'][k][j] == "M")
                      city_content = city_content + " " + "💣" + " ";
                  else if (json[i][0]['casillas'][k][j] == "A"){
                      const food = ["🍔", "🍟", "🍑", "🍇"]
                      var random = Math.floor(Math.random() * 4);
                      city_content = city_content + " " + food[random] + " ";
                  }
                  else
                      city_content = city_content + " " + json[i][0]['casillas'][k][j] + " ";
              }
              city_content = city_content + "\r\n";
          }

          //console.log(city_content)

          // pillamos los valores rgb que se pasan en el json
          r = json[i][1]['rgb'][0];
          b = json[i][1]['rgb'][1];
          g = json[i][1]['rgb'][2];

          // convertimos rgb a hexadecimal
          hex = '#' + r.toString(16) + g.toString(16) + b.toString(16);
          
          // permitimos que se respeten el formato de espacios en blanco de js en html
          city_div[i].setAttribute('style','white-space: pre;');

          // cambiamos el color de fondo segun el codigo hexadecimal
          city_div[i].style.backgroundColor = hex;

          // rellenamos con el contenido de las casillas el elemento html
          city_div[i].textContent = city_content;

      }

      // delete childs of container
      var element = document.getElementById("player-container");
      var child = element.lastElementChild; 
      while (child) {
          element.removeChild(child);
          child = element.lastElementChild;
      }

      // add childs to container
      for (let i = 4; i < json.length; i++){
          //var p = document.createElement("div");
          var alias = json[i]['alias'];
          var avatar = json[i]['avatar'];
          var ciudad = json[i]['ciudadX'] + " " + json[i]['ciudadY'];
          var x = json[i]['posX'];
          var y = json[i]['posY'];
          var nivel = json[i]['nivel'];

          var info = avatar + " " + alias + " lvl:" + nivel + " [ " + ciudad + " ] (x:" + x + ", y:" + y + ")";

          var div_player = document.createElement("div");
          div_player.classList.add('player');
          var text = document.createTextNode(info);
          div_player.appendChild(text);
          
          element.appendChild(div_player);
      }
    }catch(error){
      const err = document.querySelector('.error');
      err.style.display = 'block'

      console.log(error)
    }

  }, 1000);
})()










