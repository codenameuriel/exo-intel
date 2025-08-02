FROM python:3.10-slim
LABEL authors="urielrodriguez"

# don't compile to bytecode
ENV PYTHONDONTWRITEBYTECODE=1
# don't buffer print statement, log in real-time
ENV PYTHONUNBUFFERED=1

ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

COPY requirements.txt .

RUN pip install  --no-cache-dir -r requirements.txt

COPY . .

# gather all static files for WhiteNoise
RUN python manage.py collectstatic --noinput

# port application is listening on
EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]