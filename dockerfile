# Используем официальный Python-образ
FROM python:3.13


# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

ENV PYTHONPATH=/app



# Устанавливаем зависимости из requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем все файлы в контейнер
COPY . /app