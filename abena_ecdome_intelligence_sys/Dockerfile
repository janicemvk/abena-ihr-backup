FROM node:18-alpine

WORKDIR /app

# Copy server package.json and install server dependencies
COPY package*.json ./
RUN npm install

# Copy server files (including the updated server.js)
COPY server.js ./

# Copy React app with pre-built build folder
COPY Abena_ecdome_intelligence_sys/ ./Abena_ecdome_intelligence_sys/

EXPOSE 4005

CMD ["npm", "start"]
