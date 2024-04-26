from apscheduler.schedulers.blocking import BlockingScheduler
from convert_timestamp import convert_timestamp_to_dow_and_time

print("Running scheduler.py")

# Create a scheduler
scheduler = BlockingScheduler()

# Schedule the function to run every minute
scheduler.add_job(convert_timestamp_to_dow_and_time, 'interval', minutes=1)

# Start the scheduler
scheduler.start()
