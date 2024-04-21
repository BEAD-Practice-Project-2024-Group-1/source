FROM node:20-alpine3.18 AS BUILD

ENV NODE_OPTIONS=--max_old_space_size=8192

WORKDIR /app

COPY . .

RUN npm ci

RUN npm run build && npm prune --production

FROM node:20-alpine3.18

WORKDIR /app

COPY --from=BUILD /app ./

ENV PORT=4173

EXPOSE 4173

CMD [ "npm", "run", "prodServer" ]
