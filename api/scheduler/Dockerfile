FROM python:3.9-slim

WORKDIR /app

COPY ../api /app/api
COPY jobs_runner.py /app/scheduler/
COPY ../requirements.txt /app
COPY ../.env /app  # se precisar

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scheduler/jobs_runner.py"]
