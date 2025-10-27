# build
FROM node:20-alpine AS builder
WORKDIR /app

ARG VITE_API_BASE=http://localhost:8000/api

COPY package.json package-lock.json* ./
RUN npm ci --silent

# Copy source, inject VITE_API_BASE into .env.production before build
COPY . .

# Create .env.production used by Vite at build time
RUN echo "VITE_API_BASE=${VITE_API_BASE}" > .env.production

RUN npm run build

# serve
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]