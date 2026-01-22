FROM nginx:alpine

# Install certbot for Let's Encrypt
RUN apk add --no-cache certbot certbot-nginx

# Copy application files
COPY . /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create directory for ACME challenge
RUN mkdir -p /var/www/certbot

EXPOSE 80 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
