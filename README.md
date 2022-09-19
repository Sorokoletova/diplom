Цель проекта: cоздание веб-приложения — планировщика задач.

стек (python 3.9, Django 4.1, Postgres)

Шаги:
1) запустить БД (docker-compose up)
2) миграции
3) создать суперюзера
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Устанавливаем через pip зависимости
RUN python -m pip install --no-cache -r requirements.txt
# Копируем код приложения
COPY core core
COPY todolist todolist
COPY manage.py .

