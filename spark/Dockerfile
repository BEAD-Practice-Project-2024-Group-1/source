FROM gcr.io/datamechanics/spark:platform-3.2-latest

COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /app
RUN chmod 777 .

COPY ./*.py .
COPY postgresql-42.7.3.jar .

ENV SPARK_LOCAL_IP=${SPARK_LOCAL_IP}
ENV SCRIPT_URL=${SCRIPT_URL}
ENV USER=${USER}
ENV PASSWORD=${PASSWORD}
ENV DATABASE_HOST=${DATABASE_HOST}
ENV KAFKA_BROKER_ADDR=${KAFKA_BROKER_ADDR}

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD python3 -m flask --app main run --host=0.0.0.0 --port=8000

