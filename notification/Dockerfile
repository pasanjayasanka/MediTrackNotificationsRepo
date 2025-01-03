FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code to the container
COPY notification_service.py /app

# Install dependencies
RUN pip install flask pymysql boto3

# Expose the port the application will run on
EXPOSE 5001

# Define the command to run the application
CMD ["python", "notification_service.py"]
