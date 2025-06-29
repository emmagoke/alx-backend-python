FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Specify the command to run on container startup
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
