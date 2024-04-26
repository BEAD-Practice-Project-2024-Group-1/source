import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType

USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

# (Assuming environment variables are set for connection details)
url = f"jdbc:postgresql://{DATABASE_HOST}:5432/bead"

properties = {
    "user": USER,
    "password": PASSWORD,
    "driver": "org.postgresql.Driver",
    "stringtype": "unspecified"
}

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0') \
    .config("spark.jars", './postgresql-42.7.3.jar') \
    .master("local[*]") \
    .getOrCreate()

# Define JSON schema
json_schema = StructType([
    StructField("b_id", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("lon", FloatType(), True),
    StructField("lat", FloatType(), True),
])

# Create the streaming_df to read from kafka
streaming_df = ( spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_ADDR')) \
    .option("subscribe", "availTaxis") \
    .option("startingOffsets", "latest") \
    .load() \
    .select(F.from_json(F.col("value").cast("string"), json_schema).alias("json_data"))
)

# Select the desired columns from the parsed JSON data
df_with_columns = streaming_df.select(
    "json_data.b_id",
    "json_data.created_at",  # Assume the timestamp is in UTC "+00:00
    F.from_utc_timestamp(F.col("json_data.created_at"), "+08:00").alias("created_at_sg"),  # Convert to UTC first
    "json_data.lon",
    "json_data.lat"
)

df_with_columns = df_with_columns.dropDuplicates([ "b_id" ])

# Add columns dow and time based on the Singapore timezone
df_with_columns = df_with_columns.withColumn(
    "dow", F.dayofweek(F.col("created_at_sg"))
)
df_with_columns = df_with_columns.withColumn(
    "time", F.date_format(F.col("created_at_sg"), "HHmm")
)

df_with_columns = df_with_columns.withColumn("batch_id", F.col("b_id"))

# Select the desired columns from the parsed JSON data
df_with_columns = df_with_columns.select(
    "batch_id",
    "created_at",
    "dow",
    "time"
)

# df_with_columns = df_with_columns.groupBy("batch_id")

def foreach_batch_function(df, epoch_id):
  print("epoch_id:", epoch_id)
  df.show()
  # Transform and write the DataFrame to PostgreSQL
  df.write.jdbc(url=url, mode="append", table="processed.batch_time", properties=properties)
  pass

# print("Writing to PostgreSQL...")
df_with_columns.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()
