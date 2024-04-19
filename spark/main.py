import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

print("USER: " + USER)
print("PASSWORD: " + PASSWORD)
print("DATABASE_HOST: " + DATABASE_HOST)

# (Assuming environment variables are set for connection details)
url = f"jdbc:postgresql://{DATABASE_HOST}:5432/bead"


def read_taxi_availability():
  """
  Establishes a SparkSession, reads data from the taxi_availability table,
  and displays the results. Handles potential errors during connection or data access.

  Returns:
      None
  """

  # Create SparkSession
  spark = SparkSession.builder.appName("Spark-PostgreSQL") \
      .config("spark.jars", './postgresql-42.7.3.jar') \
      .getOrCreate()

  try:
    # Read data from PostgreSQL table
    df = spark.read.format("jdbc") \
      .option("url", url) \
      .option("driver", "org.postgresql.Driver") \
      .option("dbtable", "public.districts") \
      .option("user", USER) \
      .option("password", PASSWORD) \
      .load()

    # Display results (you can modify this section for specific formatting)
    print("Districts Data:")
    df.show(truncate=False)  # Show all rows without truncation

  except Exception as e:
    print(f"Error reading districts data: {str(e)}")

  finally:
    # Stop SparkSession
    spark.stop()

# Example usage
if __name__ == "__main__":
  read_taxi_availability()