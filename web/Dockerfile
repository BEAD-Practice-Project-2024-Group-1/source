FROM node:18.17.1-alpine3.17 AS BUILD

ENV NODE_OPTIONS=--max_old_space_size=8192

WORKDIR /app

COPY . .

RUN npm ci

RUN npm run build:ci && npm prune --production

FROM node:18.17.1-alpine3.17

WORKDIR /app

# Only copy in what we need
COPY --from=BUILD /app/build ./build
COPY --from=BUILD /app/node_modules ./node_modules
COPY package.json .


CMD [ "node", "build" ]
