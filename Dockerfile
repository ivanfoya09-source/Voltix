FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

CMD ["/bin/sh", "/app/docker/entrypoint.sh"]
