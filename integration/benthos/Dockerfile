
FROM jeffail/benthos:4.26

WORKDIR /

COPY . .

ENV SCRIPT_URL=${SCRIPT_URL}
ENV USER=${USER}
ENV PASSWORD=${PASSWORD}
ENV DATABASE_HOST=${DATABASE_HOST}
ENV KAFKA_BROKER_ADDR=${KAFKA_BROKER_ADDR}

CMD ["-c", "./config.yaml", "-r", "./resources.yaml", "streams", "./processOneMap.yaml", "./processTaxiAvailability.yaml"]