import os
from pyspark.sql import SparkSession

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

  # SQL query
  # Fetches the latest taxi availability data for each district
  # by joining the districts table with the taxi_availability table
  # and filtering the latest batch_id
  # The result is grouped by district and ordered by taxi_count in descending order
  # The taxi_count is calculated by counting the number of taxis in each district
  # whose location is within the district's geometry boundary
  # (i.e., the taxi is within the boundaries of the district)
  # The distance threshold is set to 0 for exact location matching
  # (i.e., the taxi's location must be exactly within the district's geometry boundary)
  sql_query =  """
    SELECT d.name AS district,
          COUNT(*) AS taxi_count
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
    # Fetch latest taxi availability data for each district
    print("Fetching taxi availability data...")
    results_df = spark.read.format("jdbc") \
      .option("url", url) \
      .option("driver", "org.postgresql.Driver") \
      .option("user", USER) \
      .option("password", PASSWORD) \
      .option("query", sql_query) \
      .load()
    print("Taxi availability data fetched successfully.")
    
    # Display the result
    print("Displaying result...")
    results_df.show()

  except Exception as e:
    print(f"Error reading districts data: {str(e)}")

  finally:
    # Stop SparkSession
    spark.stop()

# Example usage
if __name__ == "__main__":
  read_taxi_availability()