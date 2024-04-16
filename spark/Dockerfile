FROM gcr.io/datamechanics/spark:platform-3.2-latest

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# COPY src/ src/
COPY main.py .

ENV SPARK_LOCAL_IP=${SPARK_LOCAL_IP}

CMD python ./main.py