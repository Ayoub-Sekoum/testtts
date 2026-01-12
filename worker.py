import os
import redis
import subprocess
import sys

# Get Redis URL from environment variable
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

def main():
    """Listens for jobs on the Redis queue and executes them."""
    try:
        r = redis.from_url(REDIS_URL)
        print("Worker connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            # Wait for a job on the 'automattuner' queue
            _, job_data = r.brpop('automattuner')
            print(f"Received job: {job_data.decode('utf-8')}")

            # Placeholder for executing the automattuner logic
            # In a real implementation, you would pass the job_data
            # to the automattuner script.
            print("Executing automattuner logic...")
            # Example of how you might run the original script
            # result = subprocess.run(
            #     ['pwsh', '-File', 'automattuner/Report.py'],
            #     capture_output=True,
            #     text=True
            # )
            # print(result.stdout)
            # if result.stderr:
            #     print(result.stderr, file=sys.stderr)

            print("Job finished.")
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
