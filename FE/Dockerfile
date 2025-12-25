# ---------- build stage ----------
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- serve stage ----------
FROM nginx:1.25-alpine

# 기본 nginx 설정 제거
RUN rm -f /etc/nginx/conf.d/default.conf

# 빌드 결과물 배포
COPY --from=build /app/dist /usr/share/nginx/html

# SPA 라우팅용 nginx 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

