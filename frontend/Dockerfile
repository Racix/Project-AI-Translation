# Use an official Node.js runtime as the base image
FROM node:16

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the app's dependencies
RUN npm install

# Copy the rest of the app's files to the working directory
COPY . .

# Build the React app
RUN npm run build

# Serve the app using a simple HTTP server
FROM nginx:alpine
COPY --from=0 /usr/src/app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
