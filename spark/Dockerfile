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

CMD python ./main.py