

# Problemas encontrados y soluciones aplicadas

**Problema 1**: 

**Problema 2**: 

**Problema 3**: 

**Problema 4**: 

**Problema 5**: 

**Problema 6**: 

**Problema 7**: 

**Problema 8**: 


## Autentificación entre Players y Registry

## Auditoría de eventos en Registry

## Cifrado de los datos entre Engine y Players

## Uso de API_Rest en AA_Registry

## API_Engine

## Front

# Requirements

Install [docker](https://www.docker.com/products/docker-desktop/)

# Despliegue

En el despliegue se ha hecho uso de los contenedores de Docker. Nos hemos encotrado con problemas al asignar IP's estáticas , ya que al estar definidas en ``docker-compose.yml`` , si un servicio se quiere escalar, no sería posible ya que estaría ocupando la misma dirección IP. Para solucionar esto, dejamos que Docker sea el que nos proporcione las direcciones, ya que al permitirnos crear una red interna, sus componentes se conectan al adaptador ``Docker 0`` , que actúa como un switch, y sería la puerta por defecto de nuestra red. Al no conocer las IP's que nos van a proporcionar a nuestros servicios, tenemos el problema de que no sabemos dónde conectarnos de un módulo cliente a un módulo servidor. Para ello, se ha hecho uso de scripts, que nos filtrarán las direcciones de cada contenedor desplegado. Tras usar ``docker compose up -d --scale aa_player=x`` , no nos tendríamos que preocupar de que un mismo servicio se tenga que conectar con una IP ya usada. El parámetro ``--scale`` nos permite escalar el número de instancias de un determinado servicio.
El despliegue quedaría de la siguiente manera:


<img src=files/images/docker.jpg width=400px height=400px>


Y lo desplegaríamos ejecutando desde el directorio ``/src`` lo siguiente:
`./run.sh`

## Correr servicios

#### AA_Engine
``./run_engine``

#### AA_Weather
``./run_weather``

#### AA_Registry
``./run_registry``

#### AA_Player
``./run_player``

#### AA_NPC
``./run_npc``

#### API_Engine
``./run_api_engine``

#### Front
``./run_front``

## Parar servicios

``./stop.sh``

## Eliminar servicios

``./clean.sh``






