from pyspark.sql import SparkSession
import os

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()

# Create the streaming_df to read from kafka
streaming_df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_ADDR')) \
    .option("subscribe", "availTaxis") \
    .option("startingOffsets", "earliest") \
    .load()

# Cast the key and value columns to string
castDf = streaming_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") 

# Print the schema of the streaming_df
print("The schema of the castDf is:")
castDf.printSchema()

# Start the streaming query
query = castDf.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for the termination of the query
query.awaitTermination()
