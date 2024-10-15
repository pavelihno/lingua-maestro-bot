FROM python:3.12-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "app/app.py"]