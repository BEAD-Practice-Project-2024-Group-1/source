
FROM jeffail/benthos:4.26

COPY . .

ENV SCRIPT_URL=${SCRIPT_URL}
ENV USER=${USER}
ENV PASSWORD=${PASSWORD}
ENV DATABASE_HOST=${DATABASE_HOST}

CMD ["-c", "/config.yaml", "-r", "/resources.yaml", "streams", "/processOneMap.yaml", "/processTaxiAvailability.yaml"]