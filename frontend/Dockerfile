# Build stage
FROM node:18-alpine AS build

# Build argument for API URL (passed from docker-compose)
ARG VITE_API_BASE_URL=http://localhost:5001/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production (environment variable is baked into the build)
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
