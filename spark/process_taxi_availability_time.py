import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_utc_timestamp, date_format, dayofweek


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

print("USER: " + USER)
print("PASSWORD: " + PASSWORD)
print("DATABASE_HOST: " + DATABASE_HOST)

def process_taxi_availability_time():

    print("Beginning Taxi Availability Time Creation")
    
    # Create SparkSession
    spark = SparkSession.builder.appName("Spark-PostgreSQL") \
        .config("spark.jars", './postgresql-42.7.3.jar') \
        .getOrCreate()
    
    sql_query = f"SELECT batch_id, created_at FROM public.taxi_availability GROUP BY batch_id, created_at"

    df = spark.read.format("jdbc") \
        .option("url", url) \
        .option("driver", "org.postgresql.Driver") \
        .option("user", USER) \
        .option("password", PASSWORD) \
        .option("query", sql_query) \
        .load()
    
    df = df.withColumn("time", date_format(from_utc_timestamp(col("created_at"), "+08:00"), "HHmm"))
    df = df.withColumn("dow", dayofweek(from_utc_timestamp(col("created_at"), "+08:00")))

    df_to_write = df.select(
        "batch_id", "created_at", "dow", "time"
    )

    df_to_write.write.jdbc(url=url, mode="append", table="processed.batch_time", properties=properties)