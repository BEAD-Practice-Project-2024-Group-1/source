import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

# (Assuming environment variables are set for connection details)
url = f"jdbc:postgresql://{DATABASE_HOST}:5432/bead"

print("USER: " + USER)
print("PASSWORD: " + PASSWORD)
print("DATABASE_HOST: " + DATABASE_HOST)

def convert_timestamp_to_dow_and_time():
    """
    """

    # Create SparkSession
    spark = SparkSession.builder.appName("Convert_timestamp") \
        .config("spark.jars", './postgresql-42.7.3.jar') \
        .getOrCreate()

    # SQL statement to get latest taxi availability data 
    sql_query = """
        SELECT d.name AS district,
            COUNT(*) AS taxi_count,
            created_at
        FROM districts d
        INNER JOIN (
            SELECT location,
                batch_id
            FROM taxi_availability
            WHERE batch_id = (
                SELECT batch_id
                FROM taxi_availability
                ORDER BY created_at DESC
                LIMIT 1
            )
        ) AS latest_taxis ON ST_Distance(d.location, latest_taxis.location) <= 0
        GROUP BY d.name
        ORDER BY taxi_count DESC
    """
    try:
        # Fetch taxi_availability data
        print("Fetching taxi_availability data...")
        taxi_availability_df = spark.read \
            .format("jdbc") \
            .option("url", url) \
            .option("user", USER) \
            .option("password", PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .option("query", sql_query) \
            .load()
        print("Taxi availability data fetched successfully!")
        
        # Convert timestamp to day of week and time
        print("Converting timestamp to day of week and time...")
        taxi_availability_df = taxi_availability_df.withColumn("dow", F.dayofweek("created_at"))
        taxi_availability_df = taxi_availability_df.withColumn("time", F.date_format("created_at", "HH:mm:ss"))
        print("Timestamp converted successfully!")

        # Show the DataFrame
        print("Showing the DataFrame...")
        taxi_availability_df.show()

    except Exception as e:
        print(f"Error reading districts data: {str(e)}")
    
    finally:
        # Stop SparkSession
        spark.stop()