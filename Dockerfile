FROM python:3.11.2-slim-buster AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY . /app/

RUN pip3 install pipenv && pipenv install --system --deploy --ignore-pipfile

FROM base AS queue_bot
CMD "/app/scripts/entrypoint.sh"

FROM base AS celery_worker
COPY ./scripts/start_celery_worker.sh /scripts/start_celery_worker.sh
RUN chmod +x /scripts/start_celery_worker.sh

CMD "/scripts/start_celery_worker.sh"

FROM base AS celery_beat
COPY ./scripts/start_celery_beat.sh /scripts/start_celery_beat.sh
RUN chmod +x /scripts/start_celery_beat.sh

CMD "/scripts/start_celery_beat.sh"
