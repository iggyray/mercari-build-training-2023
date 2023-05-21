FROM node:16-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache

COPY . /app

WORKDIR /app/typescript/simple-mercari-web

RUN npm ci

RUN addgroup -S mercari && adduser -S trainee -G mercari

RUN chown -R trainee:mercari /app/typescript/simple-mercari-web

USER trainee

ENTRYPOINT ["npm", "start"]
