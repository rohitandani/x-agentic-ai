# Use Node.js as the base image
   FROM node:18-alpine

   # Set working directory
   WORKDIR /app

   # Copy package.json and install dependencies
   COPY src/dashboard/package.json ./
   RUN npm install

   # Copy the rest of the application
   COPY src/dashboard/ .

   # Build the app
   RUN npm run build

   # Expose port 3000
   EXPOSE 3000

   # Start the app
   CMD ["npm", "start"]
