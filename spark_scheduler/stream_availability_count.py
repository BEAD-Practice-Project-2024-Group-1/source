import os
from pyspark.sql import SparkSession
import pyspark.sql.types as T
import pyspark.sql.functions as F
from shapely import from_wkt

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

spark_kafka = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0') \
    .config("spark.jars", './postgresql-42.7.3.jar') \
    .master("local[*]") \
    .getOrCreate()

spark_db = SparkSession.builder.appName("District_taxi_availability") \
    .config("spark.jars", './postgresql-42.7.3.jar') \
    .getOrCreate()

districts_query = "SELECT name, ST_AsText(location) as polygon FROM districts"

districts_df = spark_db.read.format("jdbc") \
        .option("url", url) \
        .option("driver", "org.postgresql.Driver") \
        .option("user", USER) \
        .option("password", PASSWORD) \
        .option("query", districts_query) \
        .load()

# Define JSON schema
json_schema = T.StructType([
    T.StructField("b_id", T.StringType(), True),
    T.StructField("created_at", T.StringType(), True),
    T.StructField("lon", T.FloatType(), True),
    T.StructField("lat", T.FloatType(), True),
])

# Create the streaming_df to read from kafka
streaming_df = ( spark_kafka.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_ADDR')) \
    .option("subscribe", "availTaxis") \
    .option("startingOffsets", "latest") \
    .load() \
    .select(F.from_json(F.col("value").cast("string"), json_schema) \
    .alias("parsed_data")) \
    .select(F.col("parsed_data.*"))
)


@F.udf
def create_point(lon, lat):
        return f"POINT({lon} {lat})"

# @F.pandas_udf
@F.udf(returnType=T.BooleanType())
def point_in_poly(point, polygon):
    spoint = from_wkt(point)
    spolygon = from_wkt(polygon)
    return spolygon.contains(spoint)

streaming_df = streaming_df.withColumn("point", create_point(F.col("lon"), F.col("lat")))
streaming_df = streaming_df.withColumn("created_at", F.to_timestamp(F.col("created_at")))

taxi_counts_by_district = districts_df.crossJoin(streaming_df) \
    .filter( point_in_poly( F.col("point"), F.col("polygon") ) ) \
    .withWatermark("created_at", "15 seconds") \
    .groupBy( F.window( F.col("created_at"), "15 seconds" ), F.col("name") ) \
    .count()

# def foreach_batch_function(df, epoch_id):
#   print("epoch_id:", epoch_id)
#   df.show()
#   pass

taxi_counts_by_district \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get('KAFKA_BROKER_ADDR')) \
    .option("topic", "districtCounts") \
    .option("checkpointLocation", "./checkpoint") \
    .start() \
    .awaitTermination()

# print("Writing to PostgreSQL...")
# taxi_counts_by_district.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()
