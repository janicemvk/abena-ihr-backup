FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Ensure public directory exists
RUN mkdir -p public

EXPOSE 8080

CMD ["node", "server.js"]
