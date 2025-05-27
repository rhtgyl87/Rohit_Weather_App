# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py and the templates/ directory
COPY . .

# Expose port 5000, as Flask runs on this port by default
EXPOSE 5001

# Define environment variable for the API key.
# This is a placeholder; you will pass the actual key when running the container.
ENV OPENWEATHER_API_KEY="836b9dd9d83e8f864c9ad1c0c9e375a6"

# Run the Flask application
# Using 'python app.py' directly is fine for development.
# For production, consider using a production-ready WSGI server like Gunicorn.
CMD ["python", "app.py"]
