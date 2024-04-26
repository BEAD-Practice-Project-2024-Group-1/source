import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType

USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

# (Assuming environment variables are set for connection details)
url = f"jdbc:postgresql://{DATABASE_HOST}:5432/bead"

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0') \
    .config("spark.jars", './postgresql-42.7.3.jar') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()

# Define JSON schema
json_schema = StructType([
    StructField("b_id", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("lon", FloatType(), True),
    StructField("lat", FloatType(), True),
    # Add more fields as needed based on your JSON structure
])

# Create the streaming_df to read from kafka
streaming_df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_ADDR')) \
    .option("subscribe", "availTaxis") \
    .option("startingOffsets", "earliest") \
    .load() \
    .select(F.from_json(F.col("value").cast("string"), json_schema).alias("json_data")) \

# Select the desired columns from the parsed JSON data
df_with_columns = streaming_df.select(
    "json_data.b_id",
    "json_data.created_at",  # Assume the timestamp is in UTC "+00:00
    F.from_utc_timestamp(F.col("json_data.created_at"), "+08:00").alias("created_at_sg"),  # Convert to UTC first
    "json_data.lon",
    "json_data.lat"
)

# Return only first row
df_with_columns = df_with_columns.limit(1)

# Add columns dow and time based on the Singapore timezone
df_with_columns = df_with_columns.withColumn(
    "dow", F.dayofweek(F.col("created_at_sg"))
)
df_with_columns = df_with_columns.withColumn(
    "time", F.date_format(F.col("created_at_sg"), "HHmm")
)

# Select the desired columns from the parsed JSON data
df_with_columns = df_with_columns.select(
    "b_id",
    "created_at",
    "dow",
    "time"
)

# Write the processed streaming DataFrame to the database table batch_time
df_with_columns.writeStream \
    .outputMode("append") \
    .foreachBatch(lambda batch_df: batch_df.write \
        .format("jdbc") \
        .option("url", url) \
        .option("dbtable", "processed.batch_time") \
        .option("user", USER) \
        .option("password", PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .save(
            mode="append"
        ) \
        .start() 
    )

# Start the streaming query
df_with_columns.start()

# Write the processed streaming DataFrame to console, showing parsed columns
query = df_with_columns.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Write the processed streaming DataFrame to the database table batch_time
query = df_with_columns.writeStream \
    .outputMode("append") \
    .foreachBatch(lambda batch_df, batch_id: batch_df.write.jdbc(
        url=url,
        table="batch_time",
        mode="append",
        driver="org.postgresql.Driver",
        properties={"user": USER, "password": PASSWORD}
    )) \
    .start()

# Start the streaming query
query.awaitTermination()
