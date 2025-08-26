# Use official Python image instead of mise
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port Fly.io will use
EXPOSE 8080

# Run your Streamlit app
CMD ["streamlit", "run", "niles.py", "--server.port=8080", "--server.address=0.0.0.0"]
