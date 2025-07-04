# Dockerfile

# Use a lean, official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt .

# Install the Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files (the '.' means "everything in the current directory")
# into the container's /app directory.
COPY . .

# The command that will be run when the container starts.
# This "shell form" allows the ${PORT} environment variable to be correctly substituted.
CMD gunicorn --workers 3 --bind 0.0.0.0:${PORT} run:app