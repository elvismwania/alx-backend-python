# Base Image
FROM python:3.10

# Set work directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy my app code 
COPY . .

# Expose port 8000 which is default django port
EXPOSE 8000

# Command to run django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# After building, run using docker run -p 8000:8000 messaging-app
