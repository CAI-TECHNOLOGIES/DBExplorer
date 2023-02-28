FROM node:16.18.0-slim as builder


WORKDIR /opt/querybook
COPY package.json yarn.lock ./
RUN yarn install

# Copy everything else
COPY . .

RUN yarn build


FROM nginx:alpine-slim

WORKDIR /usr/share/nginx/html

RUN mkdir -p db-explorer/build
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /opt/querybook/dist/webapp db-explorer/build/
RUN mv db-explorer/build/index.html db-explorer/index.html

