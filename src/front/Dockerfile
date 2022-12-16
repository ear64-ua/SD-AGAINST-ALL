FROM node:latest

WORKDIR /usr/app
RUN npm init -y
RUN npm i express

COPY front.js /usr/app/front.js
COPY public /usr/app/public

EXPOSE 8080
