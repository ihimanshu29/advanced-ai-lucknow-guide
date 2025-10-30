# Use the full official Python runtime
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Upgrade pip inside the container (still a good practice)
RUN pip install --no-cache-dir --upgrade pip

# Install ALL Python dependencies from the EXACT requirements file
COPY requirements.txt .
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code into the container
COPY . .

# Expose the port the app runs on (FastAPI default is 8000)
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]