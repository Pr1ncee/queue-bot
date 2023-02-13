FROM python:3.10.5-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY Pipfile* ./

RUN pip3 install pipenv

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app

ENTRYPOINT ["python", "/app/scripts/main.py"]