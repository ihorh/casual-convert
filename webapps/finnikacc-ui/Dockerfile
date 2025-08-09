# packages/web/Dockerfile.dev
FROM node:24-alpine

WORKDIR /app

# Install dependencies first (so node_modules is cached)
COPY package.json package.json
COPY package-lock.json package-lock.json
COPY webapps/finnikacc-ui/package.json webapps/finnikacc-ui/package.json
RUN npm install

CMD ["npm", "run", "dev", "-w", "webapps/finnikacc-ui", "--", "--host", "0.0.0.0"]
