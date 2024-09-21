FROM python:3.11-slim-bookworm

# Stream output to console
ENV PYTHONUNBUFFERED=1

# Install poetry inside container
RUN pip install poetry==1.8.3

# Define Working Directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /app/

# Create virtual environment in container and 
# install python dependencies from the pyproject.toml
RUN poetry install

# Copy all the source code into container
COPY . /app

# Default command to execute when Docker spin-up
CMD ["poetry", "run", "python", "src/main.py"]
