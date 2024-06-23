FROM python:3.11-slim
WORKDIR /app
ENV PATROL_TOKEN=<your token>
ENV PATROL_HOST=<your host>
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./app .
CMD ["python", "kuber-patrol.py"]
