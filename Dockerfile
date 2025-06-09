# Use the official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app


# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "website.wsgi:application"]
