# Use an official Node.js runtime as the base image
FROM node:16 as builder

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

# Start a new stage from scratch
FROM nginx:alpine

# Copy the built assets from the builder stage to the nginx server directory
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# Copy the nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the outside
EXPOSE 80

# Start Nginx when the container has provisioned
CMD ["nginx", "-g", "daemon off;"]
