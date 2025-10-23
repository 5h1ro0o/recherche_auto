# frontend/Dockerfile

# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder
WORKDIR /app

# copy package files and install deps
COPY package.json package-lock.json* ./ 
# if you use pnpm/yarn, adapt accordingly
RUN npm ci --silent

# copy sources & build
COPY . .
RUN npm run build

# ---------- PRODUCTION STAGE ----------
FROM nginx:stable-alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: custom nginx config to enable SPA fallback
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
