FROM python:3.10.5

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
WORKDIR /project

ADD requirements.txt /project
RUN pip install -r requirements.txt

ADD ./project /project

CMD gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --threads 2 \
  --worker-class gthread \
  --timeout 60 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  project.wsgi:application
