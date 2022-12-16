FROM node:latest

WORKDIR /usr/app
#COPY package.json ./
RUN npm init -y
RUN npm i express
RUN npm i mongodb
RUN npm i cors
COPY api_engine.js /usr/app/api_engine.js
#RUN npm install

#COPY . .