FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY main.py /app/

RUN pip install --no-cache-dir boto3==1.28.25 requests==2.31.0 telethon==1.29.2

ENTRYPOINT ["python", "main.py"]
