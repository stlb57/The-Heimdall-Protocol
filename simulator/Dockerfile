# Use a slim Python image for a smaller container size
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
# This is the crucial step that was missing.
COPY requirements.txt ./

# Install all dependencies from the requirements file
RUN pip install -r requirements.txt

# Now copy the application file
COPY astronaut.py .

# Expose the port the Flask app will run on
EXPOSE 5001

# The command to run when the container starts
CMD ["python", "astronaut.py"]
