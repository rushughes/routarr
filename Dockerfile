FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Create necessary directories
RUN mkdir -p /incoming /watching /app/config

# Set up user and permissions
ARG UID=1000
ARG GID=1000
RUN addgroup --gid $GID appgroup && \
    adduser --disabled-password --gecos '' --uid $UID --gid $GID appuser && \
    chown -R $UID:$GID /app /incoming /watching

USER appuser

# Create migrations for the app models
RUN python manage.py makemigrations app

# Start the application using the startup script
CMD ["python", "startup.py"]
