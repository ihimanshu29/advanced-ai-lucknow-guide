# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application code into the container
COPY app.py .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8501

# Define the command to run the Streamlit application
# Use --server.address=0.0.0.0 to make it accessible outside the container
# Use --server.port to ensure it runs on the exposed port
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]