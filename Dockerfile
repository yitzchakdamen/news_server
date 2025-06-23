FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
