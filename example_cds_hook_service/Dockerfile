FROM node:22

WORKDIR /usr/src/app

COPY package*.json .
RUN npm install

COPY app.js .

CMD ["npx", "nodemon", "./app.js"]
