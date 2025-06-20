FROM node:18
WORKDIR /app
COPY src/dashboard/package.json src/dashboard/package-lock.json* ./
RUN npm install
COPY src/dashboard/ .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]