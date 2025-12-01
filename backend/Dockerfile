# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for mysql-connector-python
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Command to run the application
# CMD ["python", "run.py"]
CMD ["sh", "-c", "if [ \"$FLASK_ENV\" = \"production\" ]; then gunicorn --bind 0.0.0.0:5000 --workers 4 'app:create_app("production")'; else python run.py; fi"]
