FROM nginx:alpine

# Copy the built app
COPY dist/ /usr/share/nginx/html/

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 4009

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 