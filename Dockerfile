# Use an official Python 3.11 runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Add the requirements file to the container
ADD requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add the current directory contents into the container at /app
ADD . /app

# Create the audio directory if it doesn't exist
RUN mkdir -p /app/audio

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run the command to start uVicorn server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
