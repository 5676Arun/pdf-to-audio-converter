FROM node:16-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Create directory for client_body_temp
RUN mkdir -p /var/cache/nginx/client_body_temp

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 