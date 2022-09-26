FROM python:3.10-slim
WORKDIR /opt/todolist
ENV PIP_DISABLE_PIP_VERSION_CHECK=ON \
    PIP_NO_CACHE_DIR=off \
    PYTHON_PATH=/opt/todolist

RUN apt-get update && apt-get full-upgrade -y
RUN apt-get install -y --no-install-recommends \
    gcc\
    curl \
    build-essential \
    libpq-dev \
    && apt-get autoclean && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/var/tmp
COPY requirements.txt .
# Устанавливаем через pip зависимости
RUN python -m pip install --no-cache -r requirements.txt
# Копируем код приложения
COPY src/ .

CMD ["bash", "entrypoint.sh"]