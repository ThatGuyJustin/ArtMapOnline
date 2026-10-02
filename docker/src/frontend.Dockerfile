FROM node:24-alpine AS development-dependencies-env
COPY frontend/package.json frontend/package-lock.json /app/
WORKDIR /app
RUN npm ci

FROM node:24-alpine AS build-env
ENV NODE_PATH=/opt/node_modules
COPY --from=development-dependencies-env /app/node_modules /opt/node_modules

WORKDIR /opt/artmaponline

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8001"]
