FROM python:3.14.0-slim-bookworm
LABEL authors="Gab Lopez"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /docker

RUN apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY app/requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY app/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]