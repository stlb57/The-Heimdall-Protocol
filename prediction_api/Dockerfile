# Use a slim Python image for a smaller container size
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy all other necessary files (app.py, model.pkl) into the container
COPY . .

# Expose the port the Flask app will run on
EXPOSE 5002

# The command to run when the container starts
CMD ["python", "app.py"]
