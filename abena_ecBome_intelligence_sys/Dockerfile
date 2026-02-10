FROM node:18-alpine

WORKDIR /app

# Copy server package.json and install server dependencies
COPY package*.json ./
RUN npm install

# Copy server files (including the updated server.js)
COPY server.js ./

# Copy React app
COPY Abena_ecdome_intelligence_sys/ ./Abena_ecdome_intelligence_sys/

# Install React app dependencies and start development server
WORKDIR /app/Abena_ecdome_intelligence_sys
RUN npm install

EXPOSE 4005

# Start the React development server
CMD ["npm", "start"]
