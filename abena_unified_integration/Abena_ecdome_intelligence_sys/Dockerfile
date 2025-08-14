FROM nginx:alpine

# Copy the built React app
COPY build/ /usr/share/nginx/html/

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 4005

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 